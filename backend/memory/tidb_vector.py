from app.core.config import settings
from app.db.models.memories import Memories
from pytidb import TiDBClient, Table
from typing import List, Dict
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class TiDB:
    table: Table
    client: TiDBClient
    
    def __init__(self):
        collection_name = settings.memory_collection_name
        embedding_model_dims = settings.embedding_model_dims
        connection_string = settings.tidb_connection_string
        
        self.client = TiDBClient.connect(connection_string)

    def create_table(self):
        """
        Create memory table if not created
        """
        self.table = self.client.create_table(schema=Memories, mode="exist_ok")
    
    def insert(self, vector: List[float], payload:List[Dict]):
        """
        Insert a new memory into the table
        """
        id = str(uuid4())
        memory = Memories(id=id, vector=vector, payload=payload)
        self.table.insert(memory)
        logger.info(f"Inserted memory: {id}, payload: {payload}")
    
    def search(self, query_vector: List[float], limit: int = settings.memory_search_limit) -> List[Memories]:
        """
        Search for memories similar to the query vector
        """
        results = self.table.search(query_vector).limit(limit).to_list()
        logger.info(f"Found {len(results)} memories")
        return results
        
    def delete(self, id):
        """
        Delete a memory by its ID
        """
        self.table.delete(Memories.id == id)
        logger.info(f"Deleted memory with ID: {id}")

    def update(self, id, vector: List[float], payload: Dict):
        """
        Update a memory by its ID
        """
        values = {"vector": vector, "payload": payload}
        self.table.update(values=values, filters=Memories.id == id)
        logger.info(f"Updated memory with ID: {id}, vector: {vector}, payload: {payload}")
        
    def get(self, id) -> Dict:
        """
        Get a memory by its ID
        """
        memory = self.table.query(filters=Memories.id == id)
        if memory:
            logger.info(f"Retrieved memory with ID: {id}")
            return memory.payload
        else:
            logger.warning(f"Memory with ID: {id} not found")
            return None
