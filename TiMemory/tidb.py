from typing import List, Dict, Optional, Any
from uuid import uuid4
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, defer
from .models import Base
from .config.base import MemoryConfig
from .schemas.memory import MemoryResponse, Memory as MemorySchema

logger = logging.getLogger(__name__)

class TiDB:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.memory_model = None
        
        self._initialize_database()
        self._create_tables()
        
        from .models.memory import Memory
        self.memory_model = Memory
        
    def _initialize_database(self):
        """Initialize database connection with config"""
        try:
            logger.info(f"TiMemory connecting to database: {self.config.tidb_host}:{self.config.tidb_port}")
            self.engine = create_engine(
                self.config.tidb_connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            logger.info("TiMemory database engine created successfully")
        except Exception as e:
            logger.error(f"TiMemory failed to create database engine: {e}")
            raise
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_tables(self):
        """Create database tables if they don't exist"""
        if self.engine is None:
            raise RuntimeError("Database not initialized. Call _initialize_database() first.")
            
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            required_tables = set(Base.metadata.tables.keys())
            missing_tables = required_tables - existing_tables
            
            if missing_tables:
                logger.info(f"Creating missing TiMemory database tables: {', '.join(missing_tables)}")
                Base.metadata.create_all(bind=self.engine)
                logger.info("TiMemory database tables created successfully")
            else:
                logger.debug("All TiMemory database tables already exist")
        except Exception as e:
            logger.error(f"Error creating TiMemory database tables: {e}")
            raise

    def get_db(self):
        """Get database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call _initialize_database() first.")
            
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def insert_memory(self, vector: List[float], user_id: str, content: str, memory_attributes: Optional[Dict] = None, id: Optional[str] = None):
        """Insert a new memory into the table"""
        if id is None:
            id = str(uuid4())
        memory = self.memory_model(
            id=id,
            vector=vector,
            user_id=user_id,
            content=content,
            memory_attributes=memory_attributes or {}
        )
        
        with self.SessionLocal() as db:
            try:
                db.add(memory)
                db.commit()
                db.refresh(memory)
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to insert memory: {e}")
                raise
        return id
    
    def search_memories(self, query_vector: List[float], user_id: str, limit: int) -> MemoryResponse:
        """Search for memories similar to the query vector using cosine similarity"""
        with self.SessionLocal() as db:
            results = db.query(self.memory_model).options(defer(self.memory_model.vector)).filter(
                self.memory_model.user_id == user_id
            ).order_by(
                self.memory_model.vector.cosine_distance(query_vector)
            ).limit(limit).all()
            
            memory_schemas = [MemorySchema.model_validate(result, from_attributes=True) for result in results]
            
            logger.debug(f"Memory search returned {len(results)} results for user: {user_id}")
            return MemoryResponse(memories=memory_schemas)
    
        
    def delete_memory(self, id: str):
        """Delete a memory by its ID"""
        with self.SessionLocal() as db:
            memory = db.query(self.memory_model).filter(self.memory_model.id == id).first()
            if memory:
                db.delete(memory)
                db.commit()
                logger.info(f"Deleted memory with ID: {id}")
            else:
                logger.warning(f"Memory with ID: {id} not found")

    def update_memory(self, id: str, vector: Optional[List[float]] = None, content: Optional[str] = None, memory_attributes: Optional[Dict] = None):
        """Update a memory by its ID"""
        with self.SessionLocal() as db:
            memory = db.query(self.memory_model).filter(self.memory_model.id == id).first()
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
        
    def get_memory(self, id: str) -> Optional[Any]:
        """Get a memory by its ID"""
        with self.SessionLocal() as db:
            memory = db.query(self.memory_model).filter(self.memory_model.id == id).first()
            if memory:
                logger.info(f"Retrieved memory with ID: {id}")
                return memory
            else:
                logger.warning(f"Memory with ID: {id} not found")
                return None
    
    def get_memories_by_user(self, user_id: str, limit: Optional[int] = None) -> MemoryResponse:
        """Get all memories for a specific user"""
        with self.SessionLocal() as db:
            query = db.query(self.memory_model).filter(self.memory_model.user_id == user_id).order_by(self.memory_model.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            logger.info(f"Retrieved {len(results)} memories for user: {user_id}")
            
            memory_schemas = [MemorySchema.model_validate(result, from_attributes=True) for result in results]
            return MemoryResponse(memories=memory_schemas)

    def delete_all_memories(self, user_id: str):
        """Delete all memories for a specific user"""
        with self.SessionLocal() as db:
            deleted_count = db.query(self.memory_model).filter(self.memory_model.user_id == user_id).delete()
            db.commit()
            logger.info(f"Deleted {deleted_count} memories for user: {user_id}")