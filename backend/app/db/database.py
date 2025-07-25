from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base
import logging
import logfire

logger = logging.getLogger(__name__)
try:
    logger.info(f"Connecting to database: {settings.tidb_host}:{settings.tidb_port}")
    engine = create_engine(
        settings.tidb_connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create backend database tables (Users only) if they don't exist"""
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = set(Base.metadata.tables.keys())
        missing_tables = required_tables - existing_tables
        
        if missing_tables:
            logger.info(f"Creating missing backend database tables: {', '.join(missing_tables)}")
            Base.metadata.create_all(bind=engine)
            logger.info("Backend database tables created successfully")
        else:
            logger.debug("All backend database tables already exist")
            
        logger.info("Backend tables ready. TiMemory tables will be created when memory service is first accessed.")
        
    except Exception as e:
        logger.error(f"Error creating backend database tables: {e}")
        logger.error(f"Connection string host: {settings.tidb_host}:{settings.tidb_port}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()