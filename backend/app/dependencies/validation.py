"""
Validation dependencies for FastAPI endpoints.
"""

from app.schemas.chat import ChatRequest, MemorySearchRequest
from app.dependencies.auth import validate_user_id_match
import logging

logger = logging.getLogger(__name__)


async def validate_chat_request(user_id: str, request: ChatRequest):
    """
    Dependency for chat request validation.
    
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


async def validate_memory_search_request(user_id: str, request: MemorySearchRequest):
    """
    Dependency for memory search request validation.
    
    Args:
        user_id: User ID from URL path
        request: Memory search request object
        
    Returns:
        Validated memory search request
        
    Raises:
        ValidationException: If validation fails
    """
    validate_user_id_match(user_id, request.user_id)
    logger.debug(f"Memory search request validated for user {user_id}")
    return request