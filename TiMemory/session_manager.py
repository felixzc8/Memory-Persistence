from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_, desc
from .models import Session, Message
from .schemas.session import (
    Session as SessionSchema, 
    SessionMessage, 
    SessionSummary,
    CreateSessionRequest,
    CreateSessionResponse,
    UpdateSessionRequest
)
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Manager for user sessions and message history"""
    
    def __init__(self, db_session_factory=None):
        self.db_session_factory = db_session_factory
    
    def create_session(self, user_id: str, title: Optional[str] = None) -> CreateSessionResponse:
        """Create a new session for the user"""
        with self.db_session_factory() as db:
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
                raise Exception(f"Failed to create session for user {user_id}: {e}")
    
    def get_session(self, session_id: str) -> Optional[SessionSchema]:
        """Get session with all messages"""
        with self.db_session_factory() as db:
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
                raise Exception(
                    f"Failed to retrieve session {session_id}: {e}"
                )
    
    def get_user_sessions(self, user_id: str) -> List[SessionSummary]:
        """Get list of user's sessions (summaries only)"""
        with self.db_session_factory() as db:
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
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add message to session"""
        with self.db_session_factory() as db:
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
    
    def update_session(self, session_id: str, update_data: UpdateSessionRequest) -> bool:
        """Update session metadata"""
        with self.db_session_factory() as db:
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
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        with self.db_session_factory() as db:
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
    
    def get_session_context_with_summary(self, session_id: str, message_limit: int) -> Tuple[Optional[str], List[Dict[str, str]]]:
        """Returns (summary, recent_messages) if total > limit, else (None, all_messages)."""
        with self.db_session_factory() as db:
            total_count = db.query(Message).filter(Message.session_id == session_id).count()
            
            if total_count <= message_limit:
                return None, self.get_session_context(session_id)
            
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if not session:
                return None, []
            
            recent_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.desc()).limit(message_limit).all()
            
            recent_context = [{"role": msg.role, "content": msg.content} for msg in reversed(recent_messages)]
            return session.summary, recent_context

    def update_session_summary(self, session_id: str, summary: str, message_count: int) -> bool:
        """Store summary and update message count tracker."""
        with self.db_session_factory() as db:
            try:
                session = db.query(Session).filter(Session.session_id == session_id).first()
                if not session:
                    return False
                
                session.summary = summary
                session.last_summary_message_count = message_count
                db.commit()
                
                logger.info(f"Updated summary for session {session_id}")
                return True
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating summary for session {session_id}: {e}")
                return False

    def get_message_count(self, session_id: str) -> int:
        """Get total message count for session."""
        with self.db_session_factory() as db:
            return db.query(Message).filter(Message.session_id == session_id).count()

    def get_session_summary(self, session_id: str) -> Optional[str]:
        """Get current session summary."""
        with self.db_session_factory() as db:
            session = db.query(Session).filter(Session.session_id == session_id).first()
            return session.summary if session else None

    def should_generate_summary(self, session_id: str, message_limit: int, summary_threshold: int) -> bool:
        """Check if summary should be generated based on message count threshold."""
        with self.db_session_factory() as db:
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if not session:
                return False
            
            current_count = self.get_message_count(session_id)
            
            # First summary when limit exceeded
            if current_count > message_limit and session.summary is None:
                return True
            
            # Regenerate every summary_threshold messages after last summary
            if current_count > message_limit:
                messages_since_summary = current_count - (session.last_summary_message_count or 0)
                return messages_since_summary >= summary_threshold
            
            return False


session_manager = SessionManager()