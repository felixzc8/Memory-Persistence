"""
Authentication dependencies for FastAPI endpoints.
"""

from app.services.user_service import user_service
from app.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)


async def get_authenticated_user(user_id: str):
    """
    Dependency for user authentication and activity tracking.
    
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


def validate_user_id_match(user_id: str, request_user_id: str):
    """
    Dependency for validating user ID matches between path and request.
    
    Args:
        user_id: User ID from URL path
        request_user_id: User ID from request body
        
    Raises:
        ValidationException: If user IDs don't match
    """
    if request_user_id != user_id:
        raise ValidationException(
            "User ID mismatch between path and request body",
            error_code="USER_ID_MISMATCH",
            details={
                "path_user_id": user_id,
                "request_user_id": request_user_id
            }
        )