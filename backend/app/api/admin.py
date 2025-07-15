from fastapi import APIRouter, HTTPException
from app.services.cleanup_service import cleanup_service
from app.services.session_service import session_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/cleanup/sessions")
async def trigger_session_cleanup():
    """Manually trigger session cleanup"""
    try:
        cleaned_count = await cleanup_service.manual_cleanup()
        return {
            "message": f"Session cleanup completed",
            "sessions_cleaned": cleaned_count
        }
    except Exception as e:
        logger.error(f"Error in manual session cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/stats/sessions")
async def get_session_stats():
    """Get session statistics"""
    try:
        # This is a simple implementation - in production you'd want more detailed stats
        return {
            "message": "Session stats endpoint",
            "cleanup_interval_hours": cleanup_service.cleanup_interval / 3600,
            "session_ttl_hours": cleanup_service.session_ttl
        }
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")