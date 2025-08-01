from typing import List, Dict
from ..schemas.memory import Memory, MemoryResponse, MemoryExtractionResponse, MemoryConsolidationResponse, MemoryConsolidationItem
from ..config.base import MemoryConfig
from ..tidb import TiDB
from ..llms.openai import OpenAILLM
from ..embedding.openai import OpenAIEmbeddingModel
from ..prompts import FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT
import logging

class MemoryProcessor:
    """Handles all memory-related operations: extraction, consolidation, and storage."""
    
    def __init__(self, config: MemoryConfig, tidb: TiDB, llm: OpenAILLM, embedder: OpenAIEmbeddingModel):
        self.config = config
        self.tidb = tidb
        self.llm = llm
        self.embedder = embedder
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT
        self.logger = logging.getLogger(__name__)

    def process_memories(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Process messages for memory extraction and consolidation (used by background workers).
        """
        from uuid import uuid4
        from ..schemas.memory import MemoryAttributes
        
        self.logger.info(f"Starting memory extraction and consolidation for user {user_id} with {len(messages)} messages")
        
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
            self.logger.info(f"No similar existing memories found, storing {len(new_memories_response.memories)} new memories directly")
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in new_memories_response.memories]
            self._store_memories(memory_objects, user_id)
        else:
            self.logger.info(f"Found {len(existing_memories.memories)} similar existing memories, performing consolidation")
            consolidated_response = self._consolidate_memories(existing_memories, new_memories_response)
            self.logger.info(f"Consolidation complete, storing {len(consolidated_response.memories)} memories")
            memory_objects = [Memory(id=item.id, user_id=user_id, content=item.content, memory_attributes=item.memory_attributes) for item in consolidated_response.memories]
            self._store_memories(memory_objects, user_id)

    def search(self, query: str, user_id: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories based on a query string.
        Returns a list of Memory objects.
        """
        embedding = self.embedder.embed(query)
        results = self.tidb.search_memories(embedding, user_id, limit=limit)
        return results.memories

    def get_all_memories(self, user_id: str) -> MemoryResponse:
        """        
        Get all memories for a user.
        Returns a MemoryResponse containing a list of Memory objects.
        """
        memories = self.tidb.get_memories_by_user(user_id)
        return memories

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