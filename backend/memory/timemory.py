from .prompts import FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT
from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb_vector import TiDBVector
from typing import List, Dict
from .schemas.memories import MemoryResponse, Memory, MemoryAttributes
from uuid import uuid4
import logging
import json

class TiMem:
    def __init__(self):
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT

        self.embedder = OpenAIEmbeddingModel()
        self.llm = OpenAILLM()
        self.tidbvector = TiDBVector()
        self.tidbvector.create_table()
        self.logger = logging.getLogger(__name__)


    def _extract_memories(self, messages: List[Dict[str, str]]) -> MemoryResponse:
        """
        Extract memories from a list of messages using the fact extraction prompt.
        """
        try:
            input_data = json.dumps(messages)
            response = self.llm.generate_response(
                instructions=self.fact_extraction_prompt,
                input=input_data,
                text_format=MemoryResponse
            ).output_parsed
            self.logger.info(f"response: {response}")
            for memory in response.memories:
                memory.id = str(uuid4())
            return response
        except Exception as e:
            self.logger.error(f"Error in _extract_memories: {e}")
            raise
    
    def _consolidate_memories(self, existing_memories: MemoryResponse, new_memories: List[Memory]) -> MemoryResponse:
        """
        Resolve new memories against existing ones using the fact update memory prompt.
        """
        existing_dicts = [memory.model_dump(mode='json') for memory in existing_memories.memories]
        new_dicts = [memory.model_dump(mode='json') for memory in new_memories]
        
        input_data = json.dumps({
            "existing_memories": existing_dicts,
            "new_memories": new_dicts
        })
        
        response = self.llm.generate_response(
            instructions=self.memory_consolidation_prompt,
            input=input_data,
            text_format=MemoryResponse
        ).output_parsed
        return response

    def process_messages(self, messages: List[Dict[str, str]], user_id: str):
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, and update TiDB.
        """
        print(f"LOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGING")
        self.logger.info(f"Starting process_messages for user {user_id}")
        print(f"LOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGINGLOGGING")
        new_memories_response = self._extract_memories(messages)
        self.logger.info(f"Extracted {len(new_memories_response.memories) if new_memories_response and new_memories_response.memories else 0} memories")
        
        if not new_memories_response or not new_memories_response.memories:
            self.logger.info("No memories extracted, returning early")
            return
        
        existing_memories = self._find_similar_memories(new_memories_response.memories, user_id)
        if len(existing_memories.memories) == 0:
            self.logger.info("No similar existing memories found, storing new memories directly")
            self._store_memories(new_memories_response.memories, user_id)
            return
        consolidated_response = self._consolidate_memories(existing_memories, new_memories_response.memories)
        
        self.logger.info(f"Storing {len(consolidated_response.memories)} consolidated memories")
        self._store_memories(consolidated_response.memories, user_id)

    def _find_similar_memories(self, new_memories: List[Memory], user_id: str) -> MemoryResponse:
        """
        Find similar memories for each new memory to support consolidation.
        """
        existing_memories = []
        
        for memory in new_memories:
            embedding = self.embedder.embed(memory.content)
            similar_memories = self.tidbvector.search(embedding, user_id, limit=10)
            
            for mem in similar_memories:
                attrs = None
                if mem.memory_attributes:
                    attrs = MemoryAttributes(
                        type=mem.memory_attributes.get('type'),
                        status=mem.memory_attributes.get('status')
                    )
                
                memory_obj = Memory(
                    id=mem.id,
                    user_id=user_id,
                    content=mem.content,
                    vector=None,
                    created_at=mem.created_at,
                    updated_at=mem.updated_at,
                    memory_attributes=attrs
                )
                existing_memories.append(memory_obj)
        
        return MemoryResponse(memories=existing_memories)

    def _store_memories(self, consolidated_memories: List[Memory], user_id: str):
        """
        Store consolidated memories in TiDB. Handles new memories and updates.
        """
        for memory in consolidated_memories:
            embedding = self.embedder.embed(memory.content)
            
            # Extract type and status from memory_attributes if available
            memory_type = ''
            status = 'active'
            if memory.memory_attributes:
                memory_type = memory.memory_attributes.type or ''
                status = memory.memory_attributes.status or 'active'
            
            # Prepare metadata for storage
            metadata = {'type': memory_type, 'status': status}
            
            if status == 'outdated':
                self.tidbvector.update(
                    id=memory.id,
                    vector=embedding,
                    content=memory.content,
                    metadata=metadata
                )
            else:
                self.tidbvector.insert(
                    vector=embedding,
                    user_id=user_id,
                    content=memory.content,
                    metadata=metadata
                )

    def search(self, query: str, user_id: str, limit: int = 10) -> Dict:
        """
        Search for memories based on a query string.
        Returns a list of memory content.
        """
        embedding = self.embedder.embed(query)
        results = self.tidbvector.search(embedding, user_id, limit=limit)

        return {'results': results}

    def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.tidbvector.delete_all(user_id=user_id)