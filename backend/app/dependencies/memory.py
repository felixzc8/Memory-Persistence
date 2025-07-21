"""
Memory service guards for FastAPI endpoints.
"""

from app.services.memory_service import memory_service
from app.core.exceptions import DatabaseException
import logging

logger = logging.getLogger(__name__)


async def get_available_memory_service():
    """
    Guard for memory service availability.
    
    Returns:
        MemoryService instance if properly initialized
        
    Raises:
        DatabaseException: If memory service is not available
    """
    if not memory_service.memory:
        raise DatabaseException(
            f"Memory service not initialized: {memory_service.initialization_error or 'Unknown error'}"
        )
    
    logger.debug("Memory service availability confirmed")
    return memory_service