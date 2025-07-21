from sqlalchemy import create_engine
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
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    logfire.instrument_sqlalchemy(engine=engine)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.error(f"Connection string host: {settings.tidb_host}:{settings.tidb_port}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()