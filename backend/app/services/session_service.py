from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_, desc
from app.db.database import get_db
from app.models import Session, Message
from app.schemas.session import (
    Session as SessionSchema, 
    SessionMessage, 
    SessionSummary,
    CreateSessionRequest,
    CreateSessionResponse,
    UpdateSessionRequest
)
from app.core.exceptions import DatabaseException
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and message history"""
    
    def __init__(self):
        pass
    
    def create_session(self, user_id: str, title: Optional[str] = None) -> CreateSessionResponse:
        """Create a new session for the user"""
        db = next(get_db())
        try:
            session_id = str(uuid.uuid4())
            
            if not title:
                title = f"Session {datetime.now(timezone.utc).strftime('%b %d, %Y')}"
            
            session = Session(
                session_id=session_id,
                user_id=user_id,
                title=title
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            logger.info(f"Created session {session_id} for user {user_id}")
            
            return CreateSessionResponse(
                session_id=session_id,
                user_id=user_id,
                title=title,
                created_at=session.created_at
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating session for user {user_id}: {e}")
            raise DatabaseException(
                f"Failed to create session for user {user_id}",
                error_code="SESSION_CREATE_FAILED",
                details={"user_id": user_id, "error": str(e)}
            )
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Optional[SessionSchema]:
        """Get session with all messages"""
        db = next(get_db())
        try:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return None
            
            messages_query = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at).all()
            
            messages = [
                SessionMessage(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.created_at.isoformat()
                ) for msg in messages_query
            ]
            
            return SessionSchema(
                session_id=session.session_id,
                user_id=session.user_id,
                title=session.title,
                messages=messages,
                created_at=session.created_at,
                last_activity=session.last_activity,
                message_count=len(messages)
            )
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            raise DatabaseException(
                f"Failed to retrieve session {session_id}",
                error_code="SESSION_RETRIEVAL_FAILED",
                details={"session_id": session_id, "error": str(e)}
            )
        finally:
            db.close()
    
    def get_user_sessions(self, user_id: str) -> List[SessionSummary]:
        """Get list of user's sessions (summaries only)"""
        db = next(get_db())
        try:
            sessions = db.query(
                Session.session_id,
                Session.user_id,
                Session.title,
                Session.created_at,
                Session.last_activity
            ).filter(Session.user_id == user_id).order_by(desc(Session.last_activity)).all()
            
            summaries = []
            for sess in sessions:
                message_count = db.query(Message).filter(
                    Message.session_id == sess.session_id
                ).count()
                
                summaries.append(SessionSummary(
                    session_id=sess.session_id,
                    user_id=sess.user_id,
                    title=sess.title,
                    created_at=sess.created_at,
                    last_activity=sess.last_activity,
                    message_count=message_count,
                ))
            
            return summaries
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add message to session"""
        db = next(get_db())
        try:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content
            )
            
            db.add(message)
            
            session.last_activity = datetime.now(timezone.utc)
            
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
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            if update_data.title is not None:
                session.title = update_data.title
            
            session.last_activity = datetime.now(timezone.utc)
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
        """Delete a session and all its messages"""
        db = next(get_db())
        try:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()
            
            if not session:
                return False
            
            db.delete(session)
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
        
        messages = session.messages
        if limit and len(messages) > limit:
            messages = messages[-limit:]
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def generate_session_title(self, first_message: str) -> str:
        """Generate a session title from the first message"""
        title = first_message.strip()[:50]
        if len(first_message) > 50:
            title += "..."
        
        title = " ".join(title.split())
        
        return title if title else f"Session {datetime.now(timezone.utc).strftime('%b %d')}"
    

session_service = SessionService()