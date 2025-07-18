from app.core.config import settings
from app.models.memories import Memories
from pytidb import TiDBClient, Table
from typing import List, Dict, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class TiDBVector:
    table: Table
    client: TiDBClient
    
    def __init__(self):
        connection_string = settings.tidb_connection_string
        self.client = TiDBClient.connect(connection_string)

    def create_table(self):
        """
        Create memory table if not created
        """
        self.table = self.client.create_table(schema=Memories, mode="exist_ok")
    
    def insert(self, vector: List[float], user_id: str, content: str, metadata: Optional[Dict] = None):
        """
        Insert a new memory into the table
        """
        id = str(uuid4())
        memory = Memories(
            id=id,
            vector=vector,
            user_id=user_id,
            content=content,
            metadata=metadata or {}
        )
        self.table.insert(memory)
        logger.info(f"Inserted memory: {id}, user_id: {user_id}, content: {content[:50]}...")
        return id
    
    def search(self, query_vector: List[float], user_id: str, limit: int) -> List[Memories]:
        """
        Search for memories similar to the query vector
        """
        search_query = self.table.search(query_vector).limit(limit).filter(Memories.user_id == user_id)
        results = search_query.to_list()
        logger.info(f"Found {len(results)} memories for user: {user_id}")
        return results
        
    def delete(self, id: str):
        """
        Delete a memory by its ID
        """
        self.table.delete(Memories.id == id)
        logger.info(f"Deleted memory with ID: {id}")

    def update(self, id: str, vector: Optional[List[float]] = None, content: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Update a memory by its ID
        """
        values = {}
        if vector is not None:
            values["vector"] = vector
        if content is not None:
            values["content"] = content
        if metadata is not None:
            values["metadata"] = metadata
        
        self.table.update(values=values, filters=Memories.id == id)
        logger.info(f"Updated memory with ID: {id}")
        
    def get(self, id: str) -> Optional[Memories]:
        """
        Get a memory by its ID
        """
        results = self.table.query(filters=Memories.id == id).to_list()
        if results:
            logger.info(f"Retrieved memory with ID: {id}")
            return results[0]
        else:
            logger.warning(f"Memory with ID: {id} not found")
            return None
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Memories]:
        """
        Get all memories for a specific user
        """
        query = self.table.query(filters=Memories.user_id == user_id)
        if limit:
            query = query.limit(limit)
        
        results = query.to_list()
        logger.info(f"Retrieved {len(results)} memories for user: {user_id}")
        return results
    
    def delete_all(self, user_id: str):
        """
        Delete all memories for a specific user
        """
        self.table.delete(Memories.user_id == user_id)
        logger.info(f"Deleted all memories for user: {user_id}")
