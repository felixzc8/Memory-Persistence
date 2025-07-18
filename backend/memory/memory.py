from .prompts import SYSTEM_PROMPT, FACT_EXTRACTION_PROMPT, MEMORY_CONSOLIDATION_PROMPT
from pydantic import BaseModel
from llms.openai import OpenAILLM
from embedding.openai import OpenAIEmbeddingModel
from .tidb_vector import TiDBVector
from typing import List, Dict
from schemas.memories import MemoryResponse
from uuid import uuid4
import logging

class Memory:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.memory_consolidation_prompt = MEMORY_CONSOLIDATION_PROMPT

        self.embedder = OpenAIEmbeddingModel()
        self.llm = OpenAILLM()
        self.tidbvector = TiDBVector()
        self.tidbvector.create_table()
        self.logger = logging.getLogger(__name__)


    async def _extract_memories(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract memories from a list of messages using the fact extraction prompt.
        """
        response = self.llm.generate_response(
            instructions=self.fact_extraction_prompt,
            input=messages,
            text_format=MemoryResponse
        ).output_parsed
        for memory in response["memories"]:
            memory["id"] = str(uuid4())
        return response
    
    async def _consolidate_memories(self, existing_memories: List[Dict[str, str]], new_memories: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Resolve new memories against existing ones using the fact update memory prompt.
        """
        response = self.llm.generate_response(
            instructions=self.memory_consolidation_prompt,
            input={
                "existing_memories": existing_memories,
                "new_memories": new_memories
            },
            text_format=MemoryResponse
        ).output_parsed
        return response

    async def process_messages(self, messages: List[Dict[str, str]], user_id: str):
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, and update TiDB.
        """
        new_memories_response = self._extract_memories(messages)
        
        if not new_memories_response or not new_memories_response.get('memories'):
            return []
        
        existing_memories = self._find_similar_memories(new_memories_response['memories'], user_id)
        consolidated_response = self._consolidate_memories(existing_memories, new_memories_response['memories'])
        
        return self._store_consolidated_memories(consolidated_response['memories'], user_id)

    async def _find_similar_memories(self, new_memories: List[Dict[str, str]], user_id: str) -> List[Dict[str, str]]:
        """
        Find similar memories for each new memory to support consolidation.
        """
        existing_memories = []
        
        for memory in new_memories:
            embedding = self.embedder.embed(memory['content'])
            similar_memories = self.tidbvector.search(embedding, user_id, limit=10)
            
            for mem in similar_memories:
                existing_memories.append({
                    'id': mem.id,
                    'content': mem.content,
                    'type': mem.metadata.get('type', '') if mem.metadata else '',
                    'status': mem.metadata.get('status', 'active') if mem.metadata else 'active',
                    'created_at': mem.created_at
                })
        
        return existing_memories

    async def _store_consolidated_memories(self, consolidated_memories: List[Dict[str, str]], user_id: str) -> List[Dict[str, str]]:
        """
        Store consolidated memories in TiDB. Handles new memories and updates.
        """
        stored_memories = []
        
        for memory in consolidated_memories:
            embedding = self.embedder.embed(memory['content'])
            status = memory.get('status')
            
            if status == 'outdated':
                self.tidbvector.update(
                    id=memory['id'],
                    vector=embedding,
                    content=memory['content'],
                    metadata={'type': memory['type'], 'status': memory.get('status', 'active')}
                )
            else:
                self.tidbvector.insert(
                    vector=embedding,
                    user_id=user_id,
                    content=memory['content'],
                    metadata={'type': memory['type'], 'status': memory.get('status', 'active')}
                )
            
            stored_memories.append(memory)
        
        return stored_memories

    async def search(self, query: str, user_id: str, limit: int = 10) -> Dict:
        """
        Search for memories based on a query string.
        Returns a list of memory content.
        """
        embedding = self.embedder.embed(query)
        results = self.tidbvector.search(embedding, user_id)
        
        return {'results': results}

    async def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.tidbvector.delete_all(user_id=user_id)