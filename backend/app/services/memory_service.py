from mem0 import Memory
from typing import List, Dict, Any
from app.config import settings
from app.exceptions import DatabaseException, ChatException
import logging
import ssl

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing persistent memory using Mem0 and native TiDB Vector"""
    
    def __init__(self):
        self.memory = None
        self.initialization_error = None
        
        if settings.openai_api_key and settings.tidb_host:
            try:
                logger.info(f"Initializing memory service with TiDB: {settings.tidb_host}:{settings.tidb_port}")
                
                self.config = {
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "model": settings.model_choice,
                            "api_key": settings.openai_api_key
                        }
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {
                            "model": "text-embedding-3-small",
                            "api_key": settings.openai_api_key
                        }
                    },
                    "vector_store": {
                        "provider": "tidb",
                        "config": {
                            "host": settings.tidb_host,
                            "port": settings.tidb_port,
                            "user": settings.tidb_user,
                            "password": settings.tidb_password,
                            "database": settings.tidb_db_name,
                            "collection_name": settings.mem0_collection_name,
                            "embedding_model_dims": settings.embedding_model_dims,
                            "use_ssl": settings.tidb_use_ssl,
                            "verify_cert": settings.tidb_verify_cert,
                            "ssl_ca": settings.tidb_ssl_ca
                        }
                    }
                }
                
                self.memory = Memory.from_config(self.config)
                logger.info("Memory service initialized successfully with native TiDB Vector")
                
            except ImportError as e:
                self.initialization_error = f"Missing dependency: {str(e)}"
                logger.error(f"Memory service import error: {self.initialization_error}")
                
            except ConnectionError as e:
                self.initialization_error = f"Database connection failed: {str(e)}"
                logger.error(f"Memory service connection error: {self.initialization_error}")
                
            except ssl.SSLError as e:
                self.initialization_error = f"SSL connection failed: {str(e)}"
                logger.error(f"Memory service SSL error: {self.initialization_error}")
                
            except Exception as e:
                self.initialization_error = f"Initialization failed: {str(e)}"
                logger.error(f"Memory service error: {self.initialization_error}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                
        else:
            self.initialization_error = "Missing OpenAI API key or TiDB configuration"
            logger.error(f"Memory service not initialized: {self.initialization_error}")
    
    def search_memories(self, query: str, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for relevant memories based on query"""
        if not self.memory:
            raise DatabaseException(
                f"Memory service not initialized: {self.initialization_error or 'Unknown error'}",
                error_code="MEMORY_SERVICE_UNAVAILABLE",
                details={"user_id": user_id, "initialization_error": self.initialization_error}
            )
            
        try:
            limit = limit or settings.memory_search_limit
            result = self.memory.search(query=query, user_id=user_id, limit=limit)
            return result.get("results", [])
        except Exception as e:
            logger.error(f"Error searching memories for user {user_id}: {e}")
            raise ChatException(
                f"Memory search failed for user {user_id}",
                error_code="MEMORY_SEARCH_FAILED",
                details={"user_id": user_id, "query": query, "error": str(e)}
            )
    
    def add_memory(self, messages: List[Dict[str, str]], user_id: str) -> bool:
        """Add conversation to memory"""
        if not self.memory:
            raise DatabaseException(
                f"Memory service not initialized: {self.initialization_error or 'Unknown error'}",
                error_code="MEMORY_SERVICE_UNAVAILABLE",
                details={"user_id": user_id, "initialization_error": self.initialization_error}
            )
            
        try:
            self.memory.add(messages, user_id=user_id)
            logger.info(f"Added memory for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding memory for user {user_id}: {e}")
            raise ChatException(
                f"Memory add failed for user {user_id}",
                error_code="MEMORY_ADD_FAILED",
                details={"user_id": user_id, "error": str(e)}
            )
    
    def get_memory_context(self, query: str, user_id: str, limit: int = None) -> str:
        """Get formatted memory context for the query"""
        try:
            memories = self.search_memories(query, user_id, limit)
            if not memories:
                return "No relevant memories found."
            
            memories_str = "\n".join(f"- {entry['memory']}" for entry in memories)
            return f"User memories:\n{memories_str}"
        except (DatabaseException, ChatException):
            raise
        except Exception as e:
            logger.error(f"Error getting memory context for user {user_id}: {e}")
            raise ChatException(
                f"Memory context retrieval failed for user {user_id}",
                error_code="MEMORY_CONTEXT_FAILED",
                details={"user_id": user_id, "query": query, "error": str(e)}
            )
    
    def delete_memories(self, user_id: str) -> bool:
        """Delete all memories for a user"""
        if not self.memory:
            raise DatabaseException(
                f"Memory service not initialized: {self.initialization_error or 'Unknown error'}",
                error_code="MEMORY_SERVICE_UNAVAILABLE",
                details={"user_id": user_id, "initialization_error": self.initialization_error}
            )
            
        try:
            self.memory.delete_all(user_id=user_id)
            logger.info(f"Deleted memories for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memories for user {user_id}: {e}")
            raise ChatException(
                f"Memory delete failed for user {user_id}",
                error_code="MEMORY_DELETE_FAILED",
                details={"user_id": user_id, "error": str(e)}
            )
    
    def get_vector_store_health(self) -> Dict[str, Any]:
        """Check native TiDB Vector Store health"""
        if not self.memory:
            error_msg = f"Memory service not initialized: {self.initialization_error or 'Unknown error'}"
            return {"status": "unhealthy", "message": error_msg}
        
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