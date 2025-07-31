"""
Input validators for FastAPI endpoints.
"""

from app.schemas.chat import ChatRequest
from app.core.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)


def validate_user_id_match(user_id: str, request_user_id: str):
    """
    Validator for user ID matches between path and request body.
    
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


async def validate_chat_request(user_id: str, request: ChatRequest):
    """
    Validator for chat request validation.
    
    Args:
        user_id: User ID from URL path
        request: Chat request object
        
    Returns:
        Validated chat request
        
    Raises:
        ValidationException: If validation fails
    """
    validate_user_id_match(user_id, request.user_id)
    logger.debug(f"Chat request validated for user {user_id}")
    return request


