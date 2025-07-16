"""
Session guards for FastAPI endpoints.
"""

from app.services.session_service import session_service
from app.core.exceptions import DatabaseException, ValidationException
import logging

logger = logging.getLogger(__name__)


async def get_user_session(session_id: str, user_id: str):
    """
    Guard for session validation with user ownership.
    
    Args:
        session_id: The session ID to validate
        user_id: The user ID that should own the session
        
    Returns:
        Session object if validation successful
        
    Raises:
        DatabaseException: If session is not found
        ValidationException: If session doesn't belong to user
    """
    session = session_service.get_session(session_id)
    if not session:
        raise DatabaseException(
            f"Session not found: {session_id}",
            error_code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )
    
    if session.user_id != user_id:
        raise ValidationException(
            "Session access denied - session does not belong to user",
            error_code="SESSION_ACCESS_DENIED",
            details={
                "session_id": session_id,
                "user_id": user_id,
                "session_owner": session.user_id
            }
        )
    
    logger.info(f"Session {session_id} validated for user {user_id}")
    return session