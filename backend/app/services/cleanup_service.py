import asyncio
import logging
from datetime import datetime, timezone, timedelta
from app.services.session_service import session_service
from app.config import settings

logger = logging.getLogger(__name__)

class CleanupService:
    """Service for managing background cleanup tasks"""
    
    def __init__(self):
        self.cleanup_interval = settings.session_cleanup_interval_hours * 3600  # Convert to seconds
        self.session_ttl = settings.session_ttl_hours
        self._running = False
        self._task = None
    
    async def start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._running:
            logger.warning("Cleanup task is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started session cleanup task (interval: {self.cleanup_interval}s, TTL: {self.session_ttl}h)")
    
    async def stop_cleanup_task(self):
        """Stop the background cleanup task"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped session cleanup task")
    
    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self._running:
            try:
                # Clean up expired sessions
                cleaned_count = session_service.cleanup_expired_sessions()
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} expired sessions")
                
                # Wait for next cleanup interval
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # Wait before retrying on error
                await asyncio.sleep(60)
    
    async def manual_cleanup(self) -> int:
        """Manually trigger cleanup and return number of cleaned sessions"""
        try:
            cleaned_count = session_service.cleanup_expired_sessions()
            logger.info(f"Manual cleanup: removed {cleaned_count} expired sessions")
            return cleaned_count
        except Exception as e:
            logger.error(f"Error in manual cleanup: {e}")
            return 0

# Singleton instance
cleanup_service = CleanupService()