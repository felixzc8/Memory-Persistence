from prompts import SYSTEM_PROMPT, FACT_EXTRACTION_PROMPT, UPDATE_MEMORY_PROMPT
from pydantic import BaseModel
from llms.openai import OpenAILLM
from embedding.openai import OpenAIEmbeddingModel
from .tidb_vector import TiDBVector
from typing import List, Dict, Optional
from schemas.memories import MemoryResponse
from uuid import uuid4

class Memory:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.fact_extraction_prompt = FACT_EXTRACTION_PROMPT
        self.fact_update_memory_prompt = UPDATE_MEMORY_PROMPT

        self.embedder = OpenAIEmbeddingModel()
        self.llm = OpenAILLM()
        self.tidb = TiDBVector()
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
        for memory in response["memories"]:
            memory["id"] = str(uuid4())
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

    async def process_messages(self, messages: List[Dict[str, str]], user_id: str):
        """
        Process a conversation between user and AI assistant.
        Extract memories, consolidate with existing ones, and update TiDB.
        """
        try:
            new_memories_response = self._extract_memories(messages)
        except Exception as e:
            print(f"Error extracting memories: {e}")
            return []
        
        new_memories = new_memories_response
        if not new_memories or not new_memories.get('memories'):
            return []
        
        existing_memories = []
        for memory in new_memories['memories']:
            try:
                embedding = self.embedder.embed(memory['content'])
                similar_memories = self.tidb.search(embedding, user_id, limit=10)
            except Exception as e:
                print(f"Error processing memory embedding/search: {e}")
                continue
            
            for mem in similar_memories:
                existing_memories.append({
                    'id': mem.id,
                    'content': mem.content,
                    'type': mem.metadata.get('type', '') if mem.metadata else '',
                    'status': mem.metadata.get('status', 'active') if mem.metadata else 'active',
                    'created_at': mem.created_at
                })
        
        try:
            consolidated_response = self._consolidate_memories(existing_memories, new_memories['memories'])
        except Exception as e:
            print(f"Error consolidating memories: {e}")
            return []
        
        consolidated_memories = consolidated_response['memories']
        for memory in consolidated_memories:
            try:
                memory_dict = memory.dict() if hasattr(memory, 'dict') else memory
                embedding = self.embedder.embed(memory_dict['content'])
            except Exception as e:
                print(f"Error processing memory for storage: {e}")
                continue
            
            if 'id' in memory_dict and memory_dict['id']:
                try:
                    self.tidb.update(
                        id=memory_dict['id'],
                        vector=embedding,
                        content=memory_dict['content'],
                        metadata={'type': memory_dict['type'], 'status': memory_dict.get('status', 'active')}
                    )
                except Exception as e:
                    print(f"Error updating memory: {e}")
                    continue
            else:
                try:
                    self.tidb.insert(
                        vector=embedding,
                        user_id=user_id,
                        content=memory_dict['content'],
                        metadata={'type': memory_dict['type'], 'status': memory_dict.get('status', 'active')}
                    )
                except Exception as e:
                    print(f"Error inserting memory: {e}")
                    continue
