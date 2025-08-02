import asyncio
import logging
from typing import List, Dict
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
def process_memories(self, messages: List[Dict[str, str]], user_id: str, session_id: str):
    """
    Background task to extract and store memories from messages.
    """
    try:
        logger.info(f"Starting background memory processing for user {user_id}, session {session_id}")
        
        from ..timemory import TiMemory
        config = MemoryConfig()
        memory = TiMemory(config)
        
        memory.process_memories(messages, user_id, session_id)
        
        # Update last processed message count after successful processing
        current_message_count = memory.session_manager.get_message_count(session_id)
        memory.session_manager.update_last_memory_processed_at(session_id, current_message_count)
        logger.info(f"Updated last_memory_processed_at for session {session_id} to {current_message_count}")
        
        logger.info(f"Completed background memory processing for user {user_id}")
        return {"status": "success", "user_id": user_id, "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error in background memory processing for user {user_id}: {e}")
        self.retry(countdown=60, max_retries=3)
        raise

@celery_app.task(bind=True)
def process_summary(self, session_id: str):
    """
    Background task to generate and update conversation summary.
    """
    try:
        logger.info(f"Starting background summary processing for session {session_id}")
        
        from ..timemory import TiMemory
        config = MemoryConfig()
        memory = TiMemory(config)
        
        # Generate and update summary
        memory.generate_and_update_summary(session_id)
        
        logger.info(f"Completed background summary processing for session {session_id}")
        return {"status": "success", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error in background summary processing for session {session_id}: {e}")
        self.retry(countdown=60, max_retries=3)
        raise