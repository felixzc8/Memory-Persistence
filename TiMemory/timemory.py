from .prompts import FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT, CONVERSATION_SUMMARY_PROMPT
from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb import TiDB
from .session_manager import SessionManager
from .knowledge_graph_client import KnowledgeGraphClient
from typing import List, Dict
from .schemas.memory import Memory, MemoryExtractionResponse, MemoryConsolidationResponse, MemoryConsolidationItem, MemoryAttributes
from .config.base import MemoryConfig
from .config.timemory_config import TiMemoryConfig
from .models.message import Message

from uuid import uuid4
import logging

class TiMemory:
    def __init__(self, config: MemoryConfig):
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT
        self.conversation_summary_prompt = CONVERSATION_SUMMARY_PROMPT
        self.config = TiMemoryConfig(config)

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
        
    async def process_messages(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, update TiDB, and handle summary generation.
        """
        self.logger.info(f"Starting process_messages for user {user_id}")
        
        if session_id and await self.session_manager.should_generate_summary(
            session_id, 
            self.config.message_limit, 
            self.config.summary_threshold
        ):
            self.logger.info(f"Generating summary for session {session_id}")
            current_summary = self.session_manager.get_session_summary(session_id)
            new_summary = await self.generate_conversation_summary(session_id, current_summary)
            current_count = self.session_manager.get_message_count(session_id)
            
            summary_embedding = self.embedder.embed(new_summary.output_text)
            
            self.session_manager.create_summary(session_id, new_summary.output_text, summary_embedding, current_count)

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
    
    
    def search(self, query: str, user_id: str, limit: int = 10) -> Dict:
        """
        Search for memories based on a query string.
        Returns a list of memory content under the 'results' key.
        """
        embedding = self.embedder.embed(query)
        results = self.tidb.search_memories(embedding, user_id, limit=limit)

        return {'results': results.memories}

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

    async def generate_conversation_summary(self, session_id: str, existing_summary: str = None) -> str:
        """Generate summary from existing summary and recent chat messages."""
        
        with self.tidb.SessionLocal() as db:
            recent_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.desc()).limit(self.config.message_limit).all()
            
            recent_messages.reverse()
            
            input_messages = []
            
            if existing_summary:
                input_messages.append({"role": "system", "content": f"Existing summary: {existing_summary}"})
            
            for message in recent_messages:
                input_messages.append({"role": message.role, "content": message.content})
            
            self.logger.info(f"Generating summary with input: {input_messages}")
            
            response = self.llm.generate_response(
                instructions=self.conversation_summary_prompt,
                input=input_messages
            )
            self.logger.info(f"Generated summary response: {response}")
            return response