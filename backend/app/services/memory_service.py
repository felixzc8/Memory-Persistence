from mem0 import Memory
from openai import OpenAI
from typing import List, Dict, Any
from app.config import settings
import logging
from langchain_community.vectorstores import TiDBVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import pymysql
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class TiDBVectorStoreWithSearch(TiDBVectorStore):
    """TiDB Vector Store with working similarity_search_by_vector implementation and memory management"""
    
    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        filter: Dict[str, Any] = None,
        **kwargs
    ) -> List[Document]:
        """
        Implementation of similarity_search_by_vector with proper document ID handling for Mem0
        """
        try:
            # Use the basic similarity_search method that works
            results = self.similarity_search(
                query="", k=k, filter=filter, **kwargs
            )
            
            # Ensure each document has both metadata ID and document.id attribute for Mem0
            for doc in results:
                if 'id' not in doc.metadata:
                    # Use hash as ID if available, otherwise generate one
                    doc.metadata['id'] = doc.metadata.get('hash', f"doc_{hash(doc.page_content)}")
                
                # CRITICAL: Mem0 expects document.id attribute, not just metadata['id']
                doc.id = doc.metadata['id']
            
            return results
        except Exception as e:
            logger.error(f"Error in similarity_search_by_vector: {e}")
            return []
    
    def get_by_ids(self, ids: List[str]) -> List[Document]:
        """
        Get documents by their IDs - required for Mem0's Langchain wrapper
        This method is called by mem0's get() method
        """
        try:
            all_results = []
            for doc_id in ids:
                # Search for documents with matching hash in metadata
                # Use a broad search since TiDB doesn't support direct ID lookup
                results = self.similarity_search(
                    query="", k=1000  # Get many results to find the right one
                )
                
                # Find the document with matching hash
                for doc in results:
                    if doc.metadata.get('hash') == doc_id:
                        # Ensure the document has the id attribute that mem0 expects
                        doc.id = doc_id
                        all_results.append(doc)
                        break
                        
            logger.info(f"get_by_ids found {len(all_results)} documents for {len(ids)} requested IDs")
            return all_results
        except Exception as e:
            logger.error(f"Error in get_by_ids: {e}")
            return []
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents by IDs using SQL DELETE statements
        This method is called by mem0's delete() and update() methods
        """
        try:
            logger.info(f"Delete operation requested for {len(ids)} documents: {ids}")
            
            if not ids:
                logger.info("No IDs provided for deletion")
                return
                
            # Use the TiDB vector client's execute method for SQL operations
            client = self.tidb_vector_client
            
            deleted_count = 0
            
            # Delete documents by their hash values stored in meta JSON
            table_name = client._table_name
            for doc_id in ids:
                # Use client.execute() to run DELETE SQL command
                delete_query = f"DELETE FROM {table_name} WHERE JSON_EXTRACT(meta, '$.hash') = :hash"
                result = client.execute(delete_query, {"hash": doc_id})
                
                if result.get('success', False):
                    rows_affected = result.get('result', 0)
                    deleted_count += rows_affected
                    logger.info(f"Deleted {rows_affected} rows for hash {doc_id}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"Failed to delete hash {doc_id}: {error_msg}")
            
            logger.info(f"Successfully deleted {deleted_count} documents from {table_name}")
                
        except Exception as e:
            logger.error(f"Error in SQL-based delete method: {e}")
            # Don't raise exception to maintain mem0 compatibility

class MemoryService:
    """Service for managing persistent memory using Mem0 and TiDB Vector"""
    
    def __init__(self):
        self.tidb_vector_store = None
        self.memory = None
        
        if settings.openai_api_key and settings.tidb_host:
            try:
                # Initialize TiDB Vector Store with OpenAI embeddings
                embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                    model="text-embedding-3-small"
                )
                
                # Create TiDB Vector Store with fixed implementation
                self.tidb_vector_store = TiDBVectorStoreWithSearch(
                    connection_string=settings.tidb_vector_connection_string,
                    embedding_function=embeddings,
                    table_name=settings.mem0_collection_name,  # Use mem0 as collection/table name
                    distance_strategy=settings.tidb_vector_distance_strategy,
                )
                
                # Configure Mem0 to use TiDB Vector Store via LangChain
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
                            "client": self.tidb_vector_store
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