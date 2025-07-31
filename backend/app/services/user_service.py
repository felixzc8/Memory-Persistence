from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.db.database import get_db, engine
from app.core.exceptions import DatabaseException
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing user database operations"""
    
    def __init__(self):
        logger.info("User service initialized successfully")
    
    
    def get_db_session(self) -> Session:
        """Get database session"""
        return next(get_db())
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        try:
            db = self.get_db_session()
            user = db.query(User).filter(User.user_id == user_id).first()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise DatabaseException(
                f"Failed to retrieve user {user_id}",
                error_code="USER_RETRIEVAL_FAILED",
                details={"user_id": user_id, "error": str(e)}
            )
        finally:
            db.close()
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user"""
        try:
            db = self.get_db_session()
            existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
            if existing_user:
                logger.info(f"User {user_data.user_id} already exists")
                return existing_user
            
            new_user = User(
                user_id=user_data.user_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"Created new user: {user_data.user_id}")
            return new_user
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating user {user_data.user_id}: {e}")
            return None
        finally:
            db.close()
    
    def get_or_create_user(self, user_id: str) -> Optional[User]:
        """Get existing user or create new one if not exists"""
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
        try:
            db = self.get_db_session()
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.updated_at = datetime.now(timezone.utc)
                db.commit()
                return True
            return False
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
            return False
        finally:
            db.close()
    
    def get_database_health(self) -> dict:
        """Check database connection health"""
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                
                result = connection.execute(text("SHOW TABLES LIKE 'users'"))
                table_exists = result.fetchone() is not None
                
                from TiMemory.config.base import MemoryConfig
                memory_config = MemoryConfig()
                return {
                    "status": "healthy",
                    "database": "tidb",
                    "users_table_exists": table_exists,
                    "connection_string": memory_config.tidb_connection_string.split('@')[1]
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

user_service = UserService()