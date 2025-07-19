from memory.timem import TiMem
from typing import List, Dict, Any
from app.core.config import settings
from app.core.exceptions import ChatException
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing persistent memory using Mem0 and native TiDB Vector"""
    
    def __init__(self):
        self.memory = TiMem()
    
    
    def search_memories(self, query: str, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on query"""
        try:
            limit = limit or settings.memory_search_limit
            result = self.memory.search(query=query, user_id=user_id, limit=limit)
            return result.get("results", [])
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            raise ChatException(f"Memory search failed for user {user_id}") from e
    
    def add_memory(self, messages: List[Dict[str, str]], user_id: str) -> bool:
        """Add conversation to memory"""
        try:
            logger.info(f"Memory service add_memory called for user {user_id}")
            self.memory.process_messages(messages, user_id=user_id)
            logger.info(f"Added memory for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding memory for user {user_id}: {e}")
            raise ChatException(f"Memory add failed for user {user_id}") from e
    
    def get_memory_context(self, query: str, user_id: str, limit: int = None) -> str:
        """Format memory context for the query"""
        memories = self.search_memories(query, user_id, limit)
        if not memories:
            return "No relevant memories found."

        memories_str = "\n".join(f"- {memory.get('memory', memory.get('content', ''))}" for memory in memories)
        return f"User memories:\n{memories_str}"

    def delete_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        try:
            self.memory.delete_all(user_id=user_id)
            logger.info(f"Deleted memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memories for user {user_id}: {e}")
            raise ChatException(f"Memory delete failed for user {user_id}") from e
    
    def get_vector_store_health(self) -> Dict[str, Any]:
        """Check native TiDB Vector Store health"""
        if not self.memory:
            return {
                "status": "unhealthy", 
                "message": f"Memory service not initialized: {self.initialization_error or 'Unknown error'}"
            }
        
        try:
            vector_store_config = self.config.get("vector_store", {}).get("config", {})
            collection_info = {
                "provider": "tidb_native",
                "host": vector_store_config.get("host"),
                "database": vector_store_config.get("database"),
                "collection_name": vector_store_config.get("collection_name"),
                "embedding_dims": vector_store_config.get("embedding_model_dims"),
                "ssl_enabled": vector_store_config.get("use_ssl")
            }
            return {
                "status": "healthy",
                "vector_store": "tidb_native",
                "config": collection_info
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "message": f"Native TiDB Vector Store error: {str(e)}"
            }

memory_service = MemoryService() 