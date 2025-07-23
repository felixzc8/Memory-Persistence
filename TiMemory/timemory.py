from .prompts import FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT, CONVERSATION_SUMMARY_PROMPT
from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb_vector import TiDBVector
from .session_manager import SessionManager
from . import database
from typing import List, Dict
from .schemas.memory import MemoryResponse, Memory, MemoryExtractionResponse, MemoryConsolidationResponse, MemoryConsolidationItem, MemoryAttributes
from .config.base import MemoryConfig

from uuid import uuid4
import logging

class TiMemory:
    def __init__(self, config: MemoryConfig, message_limit: int = 20, summary_threshold: int = 10):
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT
        self.conversation_summary_prompt = CONVERSATION_SUMMARY_PROMPT
        self.config = config
        self.message_limit = message_limit
        self.summary_threshold = summary_threshold

        database.initialize_database(config)
        database.create_tables()
        
        self.embedder = OpenAIEmbeddingModel(config)
        self.llm = OpenAILLM(config)
        
        from .models.memory import Memory as MemoryModel
        self.tidbvector = TiDBVector(
            db_session_factory=database.SessionLocal,
            memory_model=MemoryModel,
            create_tables_func=database.create_tables
        )
        self.tidbvector.create_table()
        
        self.session_manager = SessionManager(
            db_session_factory=database.SessionLocal
        )
        
        self.logger = logging.getLogger(__name__)
        
    async def process_messages(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, update TiDB, and handle summary generation.
        """
        self.logger.info(f"Starting process_messages for user {user_id}")
        
        if session_id and self.session_manager.should_generate_summary(
            session_id, 
            self.message_limit, 
            self.summary_threshold
        ):
            self.logger.info(f"Generating summary for session {session_id}")
            current_summary = self.session_manager.get_session_summary(session_id)
            new_summary = await self.generate_conversation_summary(session_id, current_summary)
            current_count = self.session_manager.get_message_count(session_id)
            self.session_manager.update_session_summary(session_id, new_summary, current_count)
        
        
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
            # Convert consolidation items to Memory objects for storage
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in new_memories_response.memories]
            self._store_memories(memory_objects, user_id)
        else:
            consolidated_response = self._consolidate_memories(existing_memories, new_memories_response)
            self.logger.info(f"Storing {len(consolidated_response.memories)} consolidated memories: {consolidated_response.memories}")
            # Convert consolidation items to Memory objects for storage
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in consolidated_response.memories]
            self._store_memories(memory_objects, user_id)
    
    
    def search(self, query: str, user_id: str, limit: int = 10) -> Dict:
        """
        Search for memories based on a query string.
        Returns a list of memory content.
        """
        embedding = self.embedder.embed(query)
        results = self.tidbvector.search(embedding, user_id, limit=limit)

        return {'results': results.memories}

    def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.tidbvector.delete_all(user_id=user_id)
        
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
        existing_memories_str = "\n".join([f"EXISTING: {memory.model_dump()}" for memory in existing_memories.memories])
        new_memories_str = "\n".join([f"NEW: {memory.model_dump()}" for memory in new_memories.memories])
        input_data = f"{existing_memories_str}\n{new_memories_str}"
        
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
            similar_memories = self.tidbvector.search(embedding, user_id, limit=10)
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
                self.tidbvector.update(
                    id=memory.id,
                    vector=embedding,
                    memory_attributes=memory.memory_attributes.model_dump()
                )
            else:
                self.tidbvector.insert(
                    id=memory.id,
                    vector=embedding,
                    user_id=user_id,
                    content=memory.content,
                    memory_attributes=memory.memory_attributes.model_dump()
                )

    async def generate_conversation_summary(self, session_id: str, existing_summary: str = None) -> str:
        """Generate summary for messages beyond limit - summary_threshold to avoid knowledge gaps."""
        from .models.message import Message
        
        with database.SessionLocal() as db:
            all_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at).all()
            
            total_messages = len(all_messages)
            if total_messages <= self.message_limit:
                return existing_summary or ""

            summary_cutoff = self.message_limit - self.summary_threshold
            messages_to_summarize = all_messages[:summary_cutoff]
            
            if not messages_to_summarize:
                return existing_summary or ""
            
            conversation_data = {
                "conversation": [
                    {"role": msg.role, "content": msg.content} 
                    for msg in messages_to_summarize
                ],
                "existing_summary": existing_summary or "None"
            }
            
            response = self.llm.generate_response(
                instructions=self.conversation_summary_prompt,
                input=conversation_data
            )
            return response.response_text.strip() if hasattr(response, 'response_text') else str(response).strip()