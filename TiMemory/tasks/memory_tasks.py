import asyncio
import logging
from typing import List, Dict, Optional
from celery import Task
from ..config.base import MemoryConfig
from ..celery_app import celery_app

logger = logging.getLogger(__name__)

class AsyncTask(Task):
    def __call__(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run(*args, **kwargs))
        finally:
            loop.close()


@celery_app.task(bind=True)
def process_memories(self, messages: List[Dict[str, str]], user_id: str, session_id: Optional[str] = None):
    """
    Background task to extract and store memories from messages.
    """
    try:
        logger.info(f"Starting background memory processing for user {user_id}, session {session_id}")
        
        from ..timemory import TiMemory
        config = MemoryConfig()
        memory = TiMemory(config)
        
        memory.process_memories(messages, user_id, session_id)
        
        logger.info(f"Completed background memory processing for user {user_id}")
        return {"status": "success", "user_id": user_id, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error in background memory processing for user {user_id}: {e}")
        self.retry(countdown=60, max_retries=3)
        raise

# Removed process_summaries background task - no longer needed
# Summary generation now happens directly in topic change detection