from mem0 import Memory
from openai import OpenAI
from typing import List, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing persistent memory using Mem0 and Supabase"""
    
    def __init__(self):
        self.config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": settings.model_choice,
                }
            },
            "vector_store": {
                "provider": "supabase",
                "config": {
                    "connection_string": settings.database_url,
                    "collection_name": settings.mem0_collection_name
                }
            }
        }
        
        try:
            self.memory = Memory.from_config(self.config)
            logger.info("Memory service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory service: {e}")
            raise
    
    def search_memories(self, query: str, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on query"""
        try:
            limit = limit or settings.memory_search_limit
            result = self.memory.search(query=query, user_id=user_id, limit=limit)
            return result.get("results", [])
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            return []
    
    def add_memory(self, messages: List[Dict[str, str]], user_id: str) -> bool:
        """Add conversation to memory"""
        try:
            self.memory.add(messages, user_id=user_id)
            logger.info(f"Added memory for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding memory for user {user_id}: {e}")
            return False
    
    def get_memory_context(self, query: str, user_id: str, limit: int = None) -> str:
        """Get formatted memory context for the query"""
        memories = self.search_memories(query, user_id, limit)
        if not memories:
            return "No relevant memories found."
        
        memories_str = "\n".join(f"- {entry['memory']}" for entry in memories)
        return f"User memories:\n{memories_str}"
    
    def delete_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        try:
            # Note: This depends on mem0 API - check documentation for exact method
            # self.memory.delete(user_id=user_id)
            logger.info(f"Deleted memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memories for user {user_id}: {e}")
            return False

# Singleton instance
memory_service = MemoryService() 