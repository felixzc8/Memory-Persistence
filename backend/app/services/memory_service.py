from mem0 import Memory
from openai import OpenAI
from typing import List, Dict, Any
from app.config import settings
import logging
from langchain_community.vectorstores import TiDBVectorStore
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing persistent memory using Mem0 and TiDB Vector"""
    
    def __init__(self):
        self.tidb_vector_store = None
        self.memory = None
        
        if settings.openai_api_key and settings.tidb_host:
            try:
                # Initialize TiDB Vector Store
                embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                    model="text-embedding-3-small"
                )
                
                self.tidb_vector_store = TiDBVectorStore(
                    connection_string=settings.tidb_vector_connection_string,
                    embedding_function=embeddings,
                    table_name=settings.tidb_vector_table_name,
                    distance_strategy=settings.tidb_vector_distance_strategy,
                )
                
                # Configure Mem0 to use TiDB Vector via LangChain
                self.config = {
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "model": settings.model_choice,
                        }
                    },
                    "vector_store": {
                        "provider": "langchain",
                        "config": {
                            "collection_name": settings.mem0_collection_name,
                            "vector_store_instance": self.tidb_vector_store
                        }
                    }
                }
                
                self.memory = Memory.from_config(self.config)
                logger.info("Memory service initialized successfully with TiDB Vector")
            except Exception as e:
                logger.error(f"Failed to initialize memory service with TiDB Vector: {e}")
                self.memory = None
                self.tidb_vector_store = None
        else:
            logger.warning("Memory service not initialized - missing OpenAI API key or TiDB configuration")
    
    def search_memories(self, query: str, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on query"""
        if not self.memory:
            logger.warning("Memory service not initialized")
            return []
            
        try:
            limit = limit or settings.memory_search_limit
            result = self.memory.search(query=query, user_id=user_id, limit=limit)
            return result.get("results", [])
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            return []
    
    def add_memory(self, messages: List[Dict[str, str]], user_id: str) -> bool:
        """Add conversation to memory"""
        if not self.memory:
            logger.warning("Memory service not initialized")
            return False
            
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
        if not self.memory:
            logger.warning("Memory service not initialized")
            return False
            
        try:
            # Use Mem0's delete method to remove all memories for a user
            self.memory.delete_all(user_id=user_id)
            logger.info(f"Deleted memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memories for user {user_id}: {e}")
            return False
    
    def get_vector_store_health(self) -> Dict[str, Any]:
        """Check TiDB Vector Store health"""
        if not self.tidb_vector_store:
            return {"status": "unhealthy", "message": "TiDB Vector Store not initialized"}
        
        try:
            # Test connection by attempting a simple operation
            collection_info = {
                "table_name": settings.tidb_vector_table_name,
                "distance_strategy": settings.tidb_vector_distance_strategy,
                "connection_string": settings.tidb_vector_connection_string
            }
            return {
                "status": "healthy",
                "vector_store": "tidb",
                "config": collection_info
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "message": f"TiDB Vector Store error: {str(e)}"
            }

# Singleton instance
memory_service = MemoryService() 