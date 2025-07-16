from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, Base
from app.schemas.user import UserCreate, UserResponse
from app.config import settings
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing user database operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        
        try:
            self.engine = create_engine(
                settings.tidb_connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.debug
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._create_tables()
            
            logger.info("User service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize user service: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("User tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating user tables: {e}")
            raise
    
    def get_db_session(self) -> Session:
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        if not self.SessionLocal:
            logger.warning("Database not initialized")
            return None
        
        try:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.user_id == user_id).first()
                return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user"""
        if not self.SessionLocal:
            logger.warning("Database not initialized")
            return None
        
        try:
            with self.get_db_session() as db:
                existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
                if existing_user:
                    logger.info(f"User {user_data.user_id} already exists")
                    return existing_user
                
                new_user = User(
                    user_id=user_data.user_id,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    is_active=True
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                logger.info(f"Created new user: {user_data.user_id}")
                return new_user
                
        except SQLAlchemyError as e:
            logger.error(f"Error creating user {user_data.user_id}: {e}")
            return None
    
    def get_or_create_user(self, user_id: str) -> Optional[User]:
        """Get existing user or create new one if not exists"""
        if not self.SessionLocal:
            logger.warning("Database not initialized")
            return None
        
        try:
            user = self.get_user_by_id(user_id)
            if user:
                return user
            
            user_data = UserCreate(user_id=user_id)
            return self.create_user(user_data)
            
        except Exception as e:
            logger.error(f"Error in get_or_create_user for {user_id}: {e}")
            return None
    
    def update_user_activity(self, user_id: str) -> bool:
        """Update user's last updated timestamp"""
        if not self.SessionLocal:
            logger.warning("Database not initialized")
            return False
        
        try:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.user_id == user_id).first()
                if user:
                    user.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    return True
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
            return False
    
    def get_database_health(self) -> dict:
        """Check database connection health"""
        if not self.engine:
            return {"status": "unhealthy", "message": "Database not initialized"}
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                
                result = connection.execute(text("SHOW TABLES LIKE 'users'"))
                table_exists = result.fetchone() is not None
                
                return {
                                "status": "healthy",
            "database": "tidb",
            "users_table_exists": table_exists,
            "connection_string": settings.tidb_connection_string.split('@')[1]
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

user_service = UserService()