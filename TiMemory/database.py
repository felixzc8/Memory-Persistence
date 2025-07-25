from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base
from .config.base import MemoryConfig
import logging

logger = logging.getLogger(__name__)

# Module-level variables will be initialized when TiMemory is created
engine = None
SessionLocal = None

def initialize_database(config: MemoryConfig):
    """Initialize database connection with config"""
    global engine, SessionLocal
    
    try:
        logger.info(f"TiMemory connecting to database: {config.tidb_host}:{config.tidb_port}")
        engine = create_engine(
            config.tidb_connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        logger.info("TiMemory database engine created successfully")
    except Exception as e:
        logger.error(f"TiMemory failed to create database engine: {e}")
        raise
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables if they don't exist"""
    if engine is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = set(Base.metadata.tables.keys())
        missing_tables = required_tables - existing_tables
        
        if missing_tables:
            logger.info(f"Creating missing TiMemory database tables: {', '.join(missing_tables)}")
            Base.metadata.create_all(bind=engine)
            logger.info("TiMemory database tables created successfully")
        else:
            logger.debug("All TiMemory database tables already exist")
    except Exception as e:
        logger.error(f"Error creating TiMemory database tables: {e}")
        raise

def get_db():
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()