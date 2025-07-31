from TiMemory import TiMemory
from TiMemory.config.base import MemoryConfig
from typing import List, Dict, Any
from app.core.exceptions import ChatException
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing persistent memory using TiMemory core system"""
    
    def __init__(self):
        # TiMemory handles its own configuration from environment variables
        memory_config = MemoryConfig()
        self.memory = TiMemory(config=memory_config)
    
    
    def search_memories(self, query: str, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on query"""
        try:
            memories = self.memory.search(query=query, user_id=user_id, limit=limit)
            # Convert Memory objects to dictionaries for API response
            return [{"content": mem.content, "type": mem.memory_attributes.type} for mem in memories]
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            raise ChatException(f"Memory search failed for user {user_id}") from e
    
    
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
                "message": "Memory service not initialized"
            }
        
        try:
            config = self.memory.config
            return {
                "status": "healthy",
                "vector_store": "tidb_native",
                "config": {
                    "provider": "tidb_native",
                    "host": config.tidb_host,
                    "database": config.tidb_db_name,
                    "collection_name": config.memory_collection_name,
                    "embedding_dims": config.embedding_model_dims,
                    "ssl_enabled": config.tidb_use_ssl
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "message": f"Native TiDB Vector Store error: {str(e)}"
            }

memory_service = MemoryService() 