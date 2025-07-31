from .prompts import FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT, CONVERSATION_SUMMARY_PROMPT
from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb import TiDB
from .session_manager import SessionManager
from .knowledge_graph_client import KnowledgeGraphClient
from typing import List, Dict
from .schemas.memory import Memory, MemoryExtractionResponse, MemoryConsolidationResponse, MemoryConsolidationItem
from .config.base import MemoryConfig
from .models.message import Message
from TiMemory.tasks.memory_tasks import process_memories, process_summaries

import logging

class TiMemory:
    def __init__(self, config: MemoryConfig):
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT
        self.conversation_summary_prompt = CONVERSATION_SUMMARY_PROMPT
        self.config = config

        self.tidb = TiDB(config)
        
        self.embedder = OpenAIEmbeddingModel(config)
        self.llm = OpenAILLM(config)
        
        self.session_manager = SessionManager(
            db_session_factory=self.tidb.SessionLocal
        )
        
        self.knowledge_graph_client = KnowledgeGraphClient(
            config=self.config
        )
        
        self.logger = logging.getLogger(__name__)
        
    def queue_memory_processing(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Submit memory processing to background worker (non-blocking).
        Returns task ID for tracking.
        """
        try:
            task = process_memories.delay(messages, user_id, session_id)
            self.logger.info(f"Submitted memory processing task {task.id} for user {user_id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Failed to submit background task for user {user_id}: {e}")
            raise

    def queue_memory_extraction(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Submit memory extraction and storage to background worker (non-blocking).
        Returns task ID for tracking.
        """
        try:
            task = process_memories.delay(messages, user_id, session_id)
            self.logger.info(f"Submitted memory extraction task {task.id} for user {user_id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Failed to submit memory extraction task for user {user_id}: {e}")
            raise

    def queue_summary_processing(self, user_id: str, session_id: str):
        """
        Submit summary generation to background worker (non-blocking).
        Returns task ID for tracking.
        """
        try:
            task = process_summaries.delay(user_id, session_id)
            self.logger.info(f"Submitted summary processing task {task.id} for user {user_id}, session {session_id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Failed to submit summary processing task for user {user_id}: {e}")
            raise

    def process_memories(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Process messages for memory extraction and consolidation (used by background workers).
        """
        from uuid import uuid4
        from .schemas.memory import MemoryAttributes
        
        self.logger.info(f"Starting memory extraction and consolidation for user {user_id}")
        
        extraction_response = self._extract_memories(messages)
        self.logger.info(f"Extracted {len(extraction_response.memories)} memories: {extraction_response.memories}")
        
        if not extraction_response or not extraction_response.memories:
            self.logger.info("No memories extracted, returning without storing")
            return
        
        consolidation_items = []
        for item in extraction_response.memories:
            consolidation_item = MemoryConsolidationItem(
                id=str(uuid4()),
                content=item.content,
                memory_attributes=MemoryAttributes(
                    type=item.memory_attributes.type,
                    status="active"
                )
            )
            consolidation_items.append(consolidation_item)
        
        new_memories_response = MemoryConsolidationResponse(memories=consolidation_items)
        
        existing_memories = self._find_similar_memories(new_memories_response, user_id)
        if len(existing_memories.memories) == 0:
            self.logger.info("No similar existing memories found, storing new memories directly")
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in new_memories_response.memories]
            self._store_memories(memory_objects, user_id)
        else:
            consolidated_response = self._consolidate_memories(existing_memories, new_memories_response)
            self.logger.info(f"Storing {len(consolidated_response.memories)} consolidated memories: {consolidated_response.memories}")
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in consolidated_response.memories]
            self._store_memories(memory_objects, user_id)

    async def process_summaries(self, user_id: str, session_id: str):
        """
        Process conversation summaries and knowledge graph updates (used by background workers).
        """
        self.logger.info(f"Starting summary processing for user {user_id}, session {session_id}")
        
        if session_id and self.session_manager.should_generate_summary(
            session_id, 
            self.config.message_limit, 
            self.config.summary_threshold
        ):
            self.logger.info(f"Generating summary for session {session_id}")
            current_summary = self.session_manager.get_session_summary(session_id)
            new_summary = self.generate_conversation_summary(session_id, current_summary)
            current_count = self.session_manager.get_message_count(session_id)
            
            summary_embedding = self.embedder.embed(new_summary)
            
            self.session_manager.create_summary(session_id, new_summary, summary_embedding, current_count)

        message_count = self.session_manager.get_message_count(session_id)
        if message_count % self.config.message_limit == 0:
            try:
                recent_messages = self.session_manager.get_session_message_context(session_id, self.config.message_limit)
                await self.knowledge_graph_client.save_personal_memory(
                    chat_history=recent_messages,
                    user_id=user_id,
                    session_id=session_id
                )
                self.logger.info(f"Successfully sent summary data to knowledge graph for session {session_id}")
            except Exception as e:
                self.logger.error(f"Failed to send data to knowledge graph for session {session_id}: {e}")

    
    
    def search(self, query: str, user_id: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories based on a query string.
        Returns a list of Memory objects.
        """
        embedding = self.embedder.embed(query)
        results = self.tidb.search_memories(embedding, user_id, limit=limit)

        return results.memories

    def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.tidb.delete_all_memories(user_id=user_id)
        
    def _extract_memories(self, messages: List[Dict[str, str]]) -> MemoryExtractionResponse:
        """
        Extract memories from a list of messages using the fact extraction prompt.
        """
        self.logger.info(f"Extracting memories from messages: {messages}")
        try:
            extraction_response = self.llm.generate_parsed_response(
                instructions=self.fact_extraction_prompt,
                input=messages,
                text_format=MemoryExtractionResponse
            ).output_parsed
            self.logger.info(f"extract memory response: {extraction_response}")
            
            return extraction_response
        except Exception as e:
            self.logger.error(f"Error in _extract_memories: {e}")
            raise
        
    def _consolidate_memories(self, existing_memories: MemoryConsolidationResponse, new_memories: MemoryConsolidationResponse) -> MemoryConsolidationResponse:
        """
        Resolve new memories against existing ones using the fact update memory prompt.
        """
        existing_memories_str = "\n".join([memory.model_dump_json() for memory in existing_memories.memories])
        new_memories_str = "\n".join([memory.model_dump_json() for memory in new_memories.memories])
        input_data = f"EXISTING:\n{existing_memories_str}\nNEW:\n{new_memories_str}"
        
        self.logger.info(f"Consolidating memories: {input_data}")
        
        response = self.llm.generate_parsed_response(
            instructions=self.memory_consolidation_prompt,
            input=input_data,
            text_format=MemoryConsolidationResponse
        ).output_parsed
        self.logger.info(f"Consolidation response: {response}")
        return response

    def _find_similar_memories(self, new_memories: MemoryConsolidationResponse, user_id: str) -> MemoryConsolidationResponse:
        """
        Find similar memories for each new memory to support consolidation.
        """
        existing_memories = []
        seen_ids = set()
        
        for memory in new_memories.memories:
            embedding = self.embedder.embed(memory.content)
            similar_memories = self.tidb.search_memories(embedding, user_id, limit=self.config.memory_search_limit)
            for mem in similar_memories.memories:
                if mem.id not in seen_ids:
                    consolidation_item = MemoryConsolidationItem(
                        id=mem.id,
                        content=mem.content,
                        memory_attributes=mem.memory_attributes
                    )
                    existing_memories.append(consolidation_item)
                    seen_ids.add(mem.id)
            self.logger.info(f"Memory {memory.id} found {len(similar_memories.memories)} similar memories: {similar_memories.memories}")
        
        return MemoryConsolidationResponse(memories=existing_memories)

    def _store_memories(self, consolidated_memories: List[Memory], user_id: str):
        """
        Store consolidated memories in TiDB. Handles new memories and updates.
        """
        for memory in consolidated_memories:
            embedding = self.embedder.embed(memory.content)
            status = memory.memory_attributes.status
            
            if status == 'outdated':
                self.tidb.update_memory(
                    id=memory.id,
                    vector=embedding,
                    memory_attributes=memory.memory_attributes.model_dump()
                )
            else:
                self.tidb.insert_memory(
                    id=memory.id,
                    vector=embedding,
                    user_id=user_id,
                    content=memory.content,
                    memory_attributes=memory.memory_attributes.model_dump()
                )

    def generate_conversation_summary(self, session_id: str, existing_summary: str = None) -> str:
        """Generate summary from existing summary and recent chat messages."""
        
        with self.tidb.SessionLocal() as db:
            recent_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.desc()).limit(self.config.message_limit).all()
            
            recent_messages.reverse()
            
            conversation_text = ""
            if existing_summary:
                conversation_text += f"Existing summary: {existing_summary}\n\nRecent conversation:\n"
            else:
                conversation_text += "Conversation to summarize:\n"
            
            for message in recent_messages:
                conversation_text += f"{message.role}: {message.content}\n"
            
            self.logger.info(f"Generating summary with input: {conversation_text}")
            
            response = self.llm.generate_response(
                instructions=self.conversation_summary_prompt,
                input=conversation_text
            ).output_text
            self.logger.info(f"Generated summary response: {response}")
            return response

    async def chat_with_memory(
        self, 
        message: str, 
        user_id: str,
        request_time,
        session_id: str = None
    ) -> Dict:
        """
        Process a chat message with memory context, store the conversation, and return response
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Returns:
            Dict with assistant's response and metadata
        """
        try:
            from .prompts import SYSTEM_PROMPT
            from datetime import datetime, timezone
            
            summary = self.session_manager.get_session_summary(session_id)
            session_context = self.session_manager.get_session_message_context(
                session_id, 
                self.config.message_limit
            )
            
            memories = self.search(query=message, user_id=user_id, limit=self.config.memory_search_limit)
            memories_used = [mem.content for mem in memories]
            
            instructions = SYSTEM_PROMPT
            instructions += f"\n SUMMARY: {summary}"
            instructions += f"\n SESSION CONTEXT: {session_context}"
            user_message = [{"role": "user", "content": message}]
            
            self.logger.debug(f"LLM call context - Instructions: {instructions}, Input: {user_message}")
            
            response = self.llm.generate_response(
                instructions=instructions,
                input=user_message
            )
            
            assistant_response = response.output_text
            assistant_timestamp = datetime.now(timezone.utc)
            
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", assistant_response, assistant_timestamp)
            
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response}
            ]
            
            task_id = self.queue_memory_processing(conversation_messages, user_id, session_id)
            
            return {
                "response": assistant_response,
                "user_id": user_id,
                "session_id": session_id,
                "memories_used": memories_used,
                "timestamp": assistant_timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat_with_memory for user {user_id}: {e}")
            raise

    async def chat_with_memory_stream(
        self, 
        message: str, 
        user_id: str,
        request_time,
        session_id: str = None
    ):
        """
        Process a chat message with memory context and return streaming response
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Yields:
            Streaming response chunks
        """
        try:
            from .prompts import SYSTEM_PROMPT
            from datetime import datetime, timezone
            
            summary = self.session_manager.get_session_summary(session_id)
            session_context = self.session_manager.get_session_message_context(
                session_id, 
                self.config.message_limit
            )
            
            memories = self.search(query=message, user_id=user_id, limit=self.config.memory_search_limit)
            
            instructions = SYSTEM_PROMPT
            instructions += f"\n MEMORIES: {memories}"
            instructions += f"\n SUMMARY: {summary}"
            instructions += f"\n SESSION CONTEXT: {session_context}"
            user_message = [{"role": "user", "content": message}]
            
            self.logger.info(f"LLM streaming call context - Instructions: {instructions}, Input: {user_message}")
            
            import openai
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            stream = client.chat.completions.create(
                model=self.config.model_choice,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": message}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            assistant_timestamp = datetime.now(timezone.utc)
            
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", full_response, assistant_timestamp)
            
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": full_response}
            ]
            
            task_id = self.queue_memory_processing(conversation_messages, user_id, session_id)
            
            yield {
                "user_id": user_id,
                "session_id": session_id,
                "memories_used": memories,
                "timestamp": assistant_timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat_with_memory_stream for user {user_id}: {e}")
            raise