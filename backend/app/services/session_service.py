from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.database import Conversation, Message, get_db
from app.schemas.session import (
    Session as SessionSchema, 
    SessionMessage, 
    SessionSummary,
    CreateSessionRequest,
    CreateSessionResponse,
    UpdateSessionRequest
)
from app.config import settings
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing user sessions and conversation history"""
    
    def __init__(self):
        self.max_messages = settings.max_session_messages
    
    def create_session(self, user_id: str, title: Optional[str] = None) -> CreateSessionResponse:
        """Create a new conversation for the user"""
        db = next(get_db())
        try:
            conversation_id = str(uuid.uuid4())
            
            # Generate title from first message or use default
            if not title:
                title = f"Conversation {datetime.now(timezone.utc).strftime('%b %d, %Y')}"
            
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title
            )
            
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            
            return CreateSessionResponse(
                session_id=conversation_id,
                user_id=user_id,
                title=title,
                created_at=conversation.created_at
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating conversation for user {user_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_session(self, session_id: str) -> Optional[SessionSchema]:
        """Get conversation with all messages"""
        db = next(get_db())
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == session_id
            ).first()
            
            if not conversation:
                return None
            
            # Get messages for this conversation
            messages_query = db.query(Message).filter(
                Message.conversation_id == session_id
            ).order_by(Message.created_at).all()
            
            # Convert to SessionMessage objects
            messages = [
                SessionMessage(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.created_at.isoformat()
                ) for msg in messages_query
            ]
            
            return SessionSchema(
                session_id=conversation.id,
                user_id=conversation.user_id,
                title=conversation.title,
                messages=messages,
                created_at=conversation.created_at,
                last_activity=conversation.last_updated,
                is_active=True,  # Always active for now
                message_count=len(messages)
            )
        except Exception as e:
            logger.error(f"Error getting conversation {session_id}: {e}")
            return None
        finally:
            db.close()
    
    def get_user_sessions(self, user_id: str) -> List[SessionSummary]:
        """Get list of user's conversations (summaries only)"""
        db = next(get_db())
        try:
            # Get conversations with message counts
            conversations = db.query(
                Conversation.id,
                Conversation.user_id,
                Conversation.title,
                Conversation.created_at,
                Conversation.last_updated
            ).filter(Conversation.user_id == user_id).order_by(desc(Conversation.last_updated)).all()
            
            summaries = []
            for conv in conversations:
                # Count messages for each conversation
                message_count = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).count()
                
                summaries.append(SessionSummary(
                    session_id=conv.id,
                    user_id=conv.user_id,
                    title=conv.title,
                    created_at=conv.created_at,
                    last_activity=conv.last_updated,
                    message_count=message_count,
                    is_active=True  # Always active for now
                ))
            
            return summaries
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []
        finally:
            db.close()
    
    def add_message_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add message to conversation"""
        db = next(get_db())
        try:
            # Check if conversation exists
            conversation = db.query(Conversation).filter(
                Conversation.id == session_id
            ).first()
            
            if not conversation:
                logger.warning(f"Conversation {session_id} not found")
                return False
            
            # Handle message rotation if needed
            current_count = db.query(Message).filter(
                Message.conversation_id == session_id
            ).count()
            
            if current_count >= self.max_messages:
                # Remove oldest messages to keep within limit
                oldest_messages = db.query(Message).filter(
                    Message.conversation_id == session_id
                ).order_by(Message.created_at).limit(current_count - self.max_messages + 1).all()
                
                for msg in oldest_messages:
                    db.delete(msg)
                logger.info(f"Rotated messages for conversation {session_id}")
            
            # Create new message
            message = Message(
                id=str(uuid.uuid4()),
                conversation_id=session_id,
                role=role,
                content=content
            )
            
            db.add(message)
            
            # Update conversation last_updated timestamp
            conversation.last_updated = datetime.now(timezone.utc)
            
            db.commit()
            
            logger.info(f"Added {role} message to conversation {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding message to conversation {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def update_session(self, session_id: str, update_data: UpdateSessionRequest) -> bool:
        """Update conversation metadata"""
        db = next(get_db())
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == session_id
            ).first()
            
            if not conversation:
                return False
            
            if update_data.title is not None:
                conversation.title = update_data.title
            
            conversation.last_updated = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"Updated conversation {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating conversation {session_id}: {e}")
            return False
        finally:
            db.close()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation and all its messages"""
        db = next(get_db())
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == session_id
            ).first()
            
            if not conversation:
                return False
            
            # Messages will be deleted automatically due to CASCADE
            db.delete(conversation)
            db.commit()
            
            logger.info(f"Deleted conversation {session_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting conversation {session_id}: {e}")
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
    

# Singleton instance
session_service = SessionService()