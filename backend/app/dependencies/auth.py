"""
Authentication guards for FastAPI endpoints.
"""

from app.services.user_service import user_service
from app.core.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)


async def get_authenticated_user(user_id: str):
    """
    Guard for user authentication and activity tracking.
    
    Args:
        user_id: The user ID to authenticate
        
    Returns:
        User object if authentication successful
        
    Raises:
        ValidationException: If user authentication fails
    """
    user = user_service.get_or_create_user(user_id)
    if not user:
        raise ValidationException(
            f"Failed to authenticate user: {user_id}",
            error_code="USER_AUTH_FAILED",
            details={"user_id": user_id}
        )
    
    user_service.update_user_activity(user_id)
    logger.info(f"User {user_id} authenticated successfully")
    return user