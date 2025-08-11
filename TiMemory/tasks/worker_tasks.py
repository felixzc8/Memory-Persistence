import asyncio
import logging
from typing import List, Dict
from celery import Task
from ..config.base import MemoryConfig
from ..celery_app import celery_app
from ..tidb import TiDB
from ..embedding.openai import OpenAIEmbeddingModel
from ..llms.openai import OpenAILLM
from ..session.session_manager import SessionManager
from ..core import MemoryProcessor, SummaryProcessor
from ..schemas.memory import Memory
from ..knowledge_graph_client import KnowledgeGraphClient

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
        
        config = MemoryConfig()
        tidb = TiDB(config)
        embedder = OpenAIEmbeddingModel(config)
        llm = OpenAILLM(config)
        session_manager = SessionManager(db_session_factory=tidb.SessionLocal)
        memory_processor = MemoryProcessor(config=config, llm=llm)
        
        def search_callback(query: str, user_id: str, limit: int) -> List[Memory]:
            embedding = embedder.embed(query)
            results = tidb.search_memories(embedding, user_id, limit=limit)
            return results.memories
        
        processed_memories = memory_processor.process_memories(messages, user_id, search_callback, session_id)
        
        if processed_memories:
            _store_memories(processed_memories, user_id, tidb, embedder)
        
        current_message_count = session_manager.get_message_count(session_id)
        session_manager.update_last_memory_processed_at(session_id, current_message_count)
        logger.info(f"Updated last_memory_processed_at for session {session_id} to {current_message_count}")
        
        # Save to knowledge graph
        try:
            knowledge_graph_client = KnowledgeGraphClient(config)
            asyncio.run(knowledge_graph_client.save_personal_memory(messages, user_id, session_id))
        except Exception as e:
            logger.error(f"Failed to save personal memory to knowledge graph: {e}")
        
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
        
        config = MemoryConfig()
        tidb = TiDB(config)
        embedder = OpenAIEmbeddingModel(config)
        llm = OpenAILLM(config)
        session_manager = SessionManager(db_session_factory=tidb.SessionLocal)
        summary_processor = SummaryProcessor(config=config, llm=llm)
        
        _generate_and_update_summary(session_id, session_manager, summary_processor, embedder)
        
        logger.info(f"Completed background summary processing for session {session_id}")
        return {"status": "success", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error in background summary processing for session {session_id}: {e}")
        self.retry(countdown=60, max_retries=3)
        raise


def _store_memories(memories: List[Memory], user_id: str, tidb: TiDB, embedder: OpenAIEmbeddingModel):
    """
    Store memories in TiDB. Handles new memories and updates.
    """
    inserted_count = 0
    updated_count = 0
    
    for memory in memories:
        embedding = embedder.embed(memory.content)
        status = memory.memory_attributes.status
        
        if status == 'outdated':
            tidb.update_memory(
                id=memory.id,
                vector=embedding,
                memory_attributes=memory.memory_attributes.model_dump()
            )
            updated_count += 1
        else:
            tidb.insert_memory(
                id=memory.id,
                vector=embedding,
                user_id=user_id,
                content=memory.content,
                memory_attributes=memory.memory_attributes.model_dump()
            )
            inserted_count += 1
    
    logger.info(f"Stored {inserted_count} new and {updated_count} updated memories for user {user_id}")


def _generate_and_update_summary(session_id: str, session_manager: SessionManager, summary_processor: SummaryProcessor, embedder: OpenAIEmbeddingModel):
    """
    Generate conversation summary and update session.
    """
    current_summary = session_manager.get_session_summary(session_id)
    message_dicts = session_manager.get_session_message_context(session_id)
    
    new_summary = summary_processor.generate_conversation_summary(message_dicts, current_summary)
    
    current_message_count = session_manager.get_message_count(session_id)
    summary_embedding = embedder.embed(new_summary)
    
    session_manager.update_session_summary(
        session_id, new_summary, summary_embedding, current_message_count
    )
    
    logger.info(f"Updated session {session_id} with new summary at message count {current_message_count}")