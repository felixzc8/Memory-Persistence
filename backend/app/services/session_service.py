from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.database import SessionModel, get_db
from app.schemas.session import (
    Session as SessionSchema, 
    SessionMessage, 
    SessionSummary,
    CreateSessionRequest,
    CreateSessionResponse,
    UpdateSessionRequest
)
from app.config import settings
from datetime import datetime, timezone, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and conversation history"""
    
    def __init__(self):
        self.max_messages = settings.max_session_messages
        self.session_ttl_hours = settings.session_ttl_hours
    
    def create_session(self, user_id: str, title: Optional[str] = None) -> CreateSessionResponse:
        """Create a new session for the user"""
        db = next(get_db())
        try:
            session_id = str(uuid.uuid4())
            
            # Generate title from first message or use default
            if not title:
                title = f"Conversation {datetime.now(timezone.utc).strftime('%b %d, %Y')}"
            
            session_model = SessionModel(
                session_id=session_id,
                user_id=user_id,
                title=title,
                messages=[],
                message_count=0
            )
            
            db.add(session_model)
            db.commit()
            db.refresh(session_model)
            
            logger.info(f"Created session {session_id} for user {user_id}")
            
            return CreateSessionResponse(
                session_id=session_id,
                user_id=user_id,
                title=title,
                created_at=session_model.created_at
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating session for user {user_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Optional[SessionSchema]:
        """Get session with all messages"""
        db = next(get_db())
        try:
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session_model:
                return None
            
            # Convert JSON messages to SessionMessage objects
            messages = [
                SessionMessage(**msg) for msg in session_model.messages
            ]
            
            return SessionSchema(
                session_id=session_model.session_id,
                user_id=session_model.user_id,
                title=session_model.title,
                messages=messages,
                created_at=session_model.created_at,
                last_activity=session_model.last_activity,
                is_active=session_model.is_active,
                message_count=session_model.message_count
            )
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
        finally:
            db.close()
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[SessionSummary]:
        """Get list of user's sessions (summaries only)"""
        db = next(get_db())
        try:
            query = db.query(SessionModel).filter(SessionModel.user_id == user_id)
            
            if active_only:
                query = query.filter(SessionModel.is_active == True)
            
            sessions = query.order_by(desc(SessionModel.last_activity)).all()
            
            return [
                SessionSummary(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    title=session.title,
                    created_at=session.created_at,
                    last_activity=session.last_activity,
                    message_count=session.message_count,
                    is_active=session.is_active
                )
                for session in sessions
            ]
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add message to session with automatic rotation if needed"""
        db = next(get_db())
        try:
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session_model:
                logger.warning(f"Session {session_id} not found")
                return False
            
            # Create new message
            new_message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Get current messages
            messages = session_model.messages or []
            messages.append(new_message)
            
            # Rotate messages if exceeding limit
            if len(messages) > self.max_messages:
                # Remove oldest messages to keep within limit
                messages = messages[-self.max_messages:]
                logger.info(f"Rotated messages for session {session_id}, kept {len(messages)} messages")
            
            # Update session
            session_model.messages = messages
            session_model.message_count = len(messages)
            session_model.last_activity = datetime.now(timezone.utc)
            
            db.commit()
            
            logger.info(f"Added {role} message to session {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def update_session(self, session_id: str, update_data: UpdateSessionRequest) -> bool:
        """Update session metadata"""
        db = next(get_db())
        try:
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session_model:
                return False
            
            if update_data.title is not None:
                session_model.title = update_data.title
            
            if update_data.is_active is not None:
                session_model.is_active = update_data.is_active
            
            session_model.last_activity = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating session {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        db = next(get_db())
        try:
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if not session_model:
                return False
            
            db.delete(session_model)
            db.commit()
            
            logger.info(f"Deleted session {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def get_session_context(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get session messages formatted for OpenAI context"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Limit messages if specified
        messages = session.messages
        if limit and len(messages) > limit:
            messages = messages[-limit:]
        
        # Format for OpenAI API
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def generate_session_title(self, first_message: str) -> str:
        """Generate a session title from the first message"""
        # Truncate and clean up the message for title
        title = first_message.strip()[:50]
        if len(first_message) > 50:
            title += "..."
        
        # Remove newlines and clean up
        title = " ".join(title.split())
        
        return title if title else f"Conversation {datetime.now(timezone.utc).strftime('%b %d')}"
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (older than TTL)"""
        db = next(get_db())
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.session_ttl_hours)
            
            expired_sessions = db.query(SessionModel).filter(
                SessionModel.last_activity < cutoff_time
            ).all()
            
            count = len(expired_sessions)
            
            for session in expired_sessions:
                db.delete(session)
            
            db.commit()
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
            
            return count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
        finally:
            db.close()

# Singleton instance
session_service = SessionService()