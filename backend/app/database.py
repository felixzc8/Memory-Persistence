from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(36), primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    messages = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_activity = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)

# Database connection
engine = create_engine(
    settings.tidb_connection_string,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()