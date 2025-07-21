from app.core.config import settings
from app.models.memory import Memory
from app.db.database import SessionLocal, create_tables
from sqlalchemy.orm import Session, defer
from sqlalchemy import func
from typing import List, Dict, Optional
from uuid import uuid4
import logging
from app.schemas.memory import MemoryResponse, Memory as MemorySchema

logger = logging.getLogger(__name__)

class TiDBVector:
    
    def __init__(self):
        # Ensure tables are created
        create_tables()

    def create_table(self):
        """
        Create memory table if not created - handled by create_tables()
        """
        pass
    
    def insert(self, vector: List[float], user_id: str, content: str, memory_attributes: Optional[Dict] = None, id: Optional[str] = None):
        """
        Insert a new memory into the table
        """
        if id is None:
            id = str(uuid4())
        memory = Memory(
            id=id,
            vector=vector,
            user_id=user_id,
            content=content,
            memory_attributes=memory_attributes or {}
        )
        
        with SessionLocal() as db:
            try:
                db.add(memory)
                db.commit()
                db.refresh(memory)
                logger.info(f"Successfully inserted memory: {id}, user_id: {user_id}, content: {content[:50]}...")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to insert memory: {e}")
                raise
        return id
    
    def search(self, query_vector: List[float], user_id: str, limit: int) -> MemoryResponse:
        """
        Search for memories similar to the query vector using cosine similarity
        """
        with SessionLocal() as db:
            results = db.query(Memory).options(defer(Memory.vector)).filter(
                Memory.user_id == user_id
            ).order_by(
                Memory.vector.cosine_distance(query_vector)
            ).limit(limit).all()
            
            memory_schemas = [MemorySchema.model_validate(result, from_attributes=True) for result in results]
            
            logger.info(f"Found {len(results)} memories for user: {user_id}: {memory_schemas}")
            return MemoryResponse(memories=memory_schemas)
        
    def delete(self, id: str):
        """
        Delete a memory by its ID
        """
        with SessionLocal() as db:
            memory = db.query(Memory).filter(Memory.id == id).first()
            if memory:
                db.delete(memory)
                db.commit()
                logger.info(f"Deleted memory with ID: {id}")
            else:
                logger.warning(f"Memory with ID: {id} not found")

    def update(self, id: str, vector: Optional[List[float]] = None, content: Optional[str] = None, memory_attributes: Optional[Dict] = None):
        """
        Update a memory by its ID
        """
        with SessionLocal() as db:
            memory = db.query(Memory).filter(Memory.id == id).first()
            if memory:
                if vector is not None:
                    memory.vector = vector
                if content is not None:
                    memory.content = content
                if memory_attributes is not None:
                    memory.memory_attributes = memory_attributes
                
                db.commit()
                logger.info(f"Updated memory with ID: {id}")
            else:
                logger.warning(f"Memory with ID: {id} not found")
        
    def get(self, id: str) -> Optional[Memory]:
        """
        Get a memory by its ID
        """
        with SessionLocal() as db:
            memory = db.query(Memory).filter(Memory.id == id).first()
            if memory:
                logger.info(f"Retrieved memory with ID: {id}")
                return memory
            else:
                logger.warning(f"Memory with ID: {id} not found")
                return None
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Memory]:
        """
        Get all memories for a specific user
        """
        with SessionLocal() as db:
            query = db.query(Memory).filter(Memory.user_id == user_id).order_by(Memory.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            logger.info(f"Retrieved {len(results)} memories for user: {user_id}")
            return results
    
    def delete_all(self, user_id: str):
        """
        Delete all memories for a specific user
        """
        with SessionLocal() as db:
            deleted_count = db.query(Memory).filter(Memory.user_id == user_id).delete()
            db.commit()
            logger.info(f"Deleted {deleted_count} memories for user: {user_id}")
