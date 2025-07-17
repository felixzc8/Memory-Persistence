from prompts import SYSTEM_PROMPT, FACT_EXTRACTION_PROMPT, UPDATE_MEMORY_PROMPT
from pydantic import BaseModel
from llms import OpenAILLM
from embedding import OpenAIEmbeddingModel
from tidb_vector import TiDB
from typing import List, Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from schemas.memories import MemoryResponse

class Memory:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.fact_update_memory_prompt = UPDATE_MEMORY_PROMPT

        self.embedder = OpenAIEmbeddingModel()
        self.llm = OpenAILLM()
        self.tidb = TiDB()
        self.tidb.create_table()


    def _extract_memories(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract memories from a list of messages using the fact extraction prompt.
        """
        response = self.llm.generate_response(
            instructions=self.fact_extraction_prompt,
            input=messages,
            text_format=MemoryResponse
        )
        for memory in response.memories:
            memory['created_at'] = datetime.now(ZoneInfo("Asia/Hong_Kong"))
            memory['status'] = 'active'
        return response
    
    def _consolidate_memories(self, existing_memories: List[Dict[str, str]], new_memories: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Resolve new memories against existing ones using the fact update memory prompt.
        """
        response = self.llm.generate_response(
            instructions=self.fact_update_memory_prompt,
            input={
                "existing_memories": existing_memories,
                "new_memories": new_memories
            },
            text_format=MemoryResponse
        )
        return response

    def process_messages(self, messages: List[Dict[str, str]], user_id: str) -> List[Dict[str, str]]:
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, and update TiDB.
        """
        # Extract new memories from the conversation
        new_memories_response = self._extract_memories(messages)
        new_memories = new_memories_response.facts
        
        if not new_memories:
            return []
        
        # Get existing memories for the user by searching with embeddings
        existing_memories = []
        for memory in new_memories:
            # Generate embedding for the memory content
            embedding = self.embedder.embed_query(memory.content)
            # Search for similar existing memories
            similar_memories = self.tidb.search(embedding, limit=10)
            
            # Filter by user_id and convert to dict format
            user_memories = []
            for mem in similar_memories:
                if mem.user_id == user_id:
                    user_memories.append({
                        'id': mem.id,
                        'content': mem.payload.get('content', ''),
                        'type': mem.payload.get('type', ''),
                        'status': mem.payload.get('status', 'active'),
                        'created_at': mem.created_at
                    })
            existing_memories.extend(user_memories)
        
        # Consolidate new memories with existing ones
        consolidated_response = self._consolidate_memories(existing_memories, [m.dict() for m in new_memories])
        consolidated_memories = consolidated_response.facts
        
        # Update TiDB with consolidated memories
        for memory in consolidated_memories:
            memory_dict = memory.dict() if hasattr(memory, 'dict') else memory
            embedding = self.embedder.embed_query(memory_dict['content'])
            
            payload = {
                'content': memory_dict['content'],
                'type': memory_dict['type'],
                'status': memory_dict.get('status', 'active'),
                'user_id': user_id
            }
            
            # Check if this is an update to existing memory or new memory
            if 'id' in memory_dict and memory_dict['id']:
                # Update existing memory
                self.tidb.update(memory_dict['id'], embedding, payload)
            else:
                # Insert new memory
                self.tidb.insert(embedding, payload)
        
        return [m.dict() if hasattr(m, 'dict') else m for m in consolidated_memories]

