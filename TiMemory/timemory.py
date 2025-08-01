from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb import TiDB
from .session.session_manager import SessionManager
from .knowledge_graph_client import KnowledgeGraphClient
from typing import List, Dict
from .schemas.memory import Memory, MemoryResponse
from .config.base import MemoryConfig
from TiMemory.tasks.memory_tasks import process_memories
from .core import MemoryProcessor, ChatService, SummaryService, TopicDetector

import logging

class TiMemory:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core dependencies
        self._setup_services()
        
    def _setup_services(self):
        """Initialize all services and their dependencies."""
        # Core infrastructure
        self.tidb = TiDB(self.config)
        self.embedder = OpenAIEmbeddingModel(self.config)
        self.llm = OpenAILLM(self.config)
        
        # Session management
        self.session_manager = SessionManager(
            db_session_factory=self.tidb.SessionLocal
        )
        
        # Core services
        self.memory_processor = MemoryProcessor(
            config=self.config,
            tidb=self.tidb,
            llm=self.llm,
            embedder=self.embedder
        )
        
        self.summary_service = SummaryService(
            config=self.config,
            llm=self.llm,
            tidb=self.tidb,
            embedder=self.embedder
        )
        
        self.topic_detector = TopicDetector(
            config=self.config,
            llm=self.llm,
            session_manager=self.session_manager,
            memory_processor=self.memory_processor,
            summary_service=self.summary_service
        )
        
        self.chat_service = ChatService(
            config=self.config,
            llm=self.llm,
            memory_processor=self.memory_processor,
            session_manager=self.session_manager,
            topic_detector=self.topic_detector
        )
        
        # Optional knowledge graph client
        self.knowledge_graph_client = KnowledgeGraphClient(
            config=self.config
        )
        
    def queue_memory_processing(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Submit memory processing to background worker (non-blocking).
        Returns task ID for tracking.
        """
        try:
            task = process_memories.delay(messages, user_id, session_id)
            self.logger.info(f"Submitted memory processing task {task.id} for user {user_id}")
            return task.id
        except Exception as e:
            self.logger.error(f"Failed to submit background task for user {user_id}: {e}")
            raise


    def process_memories(self, messages: List[Dict[str, str]], user_id: str, session_id: str = None):
        """
        Process messages for memory extraction and consolidation (used by background workers).
        """
        return self.memory_processor.process_memories(messages, user_id, session_id)

    def search(self, query: str, user_id: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories based on a query string.
        Returns a list of Memory objects.
        """
        return self.memory_processor.search(query, user_id, limit)

    def get_all_memories(self, user_id: str) -> MemoryResponse:
        """        
        Get all memories for a user.
        Returns a MemoryResponse containing a list of Memory objects.
        """
        return self.memory_processor.get_all_memories(user_id)

    def get_all_memories(self, user_id: str) -> MemoryResponse:
        """        Get all memories for a user.
        Returns a MemoryResponse containing a list of Memory objects.
        """
        memories = self.tidb.get_memories_by_user(user_id)
        return memories

    def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.memory_processor.delete_all(user_id)

    def check_and_process_topic_change(self, user_id: str, session_id: str) -> bool:
        """
        Check for topic changes and trigger memory/summary processing if needed.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            bool: True if topic change was detected and processing triggered
        """
        return self.topic_detector.check_and_process_topic_change(user_id, session_id)

    async def chat_with_memory(
        self, 
        message: str, 
        user_id: str,
        request_time,
        session_id: str = None
    ) -> Dict:
        """
        Process a chat message with memory context, store the conversation, and return response
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Returns:
            Dict with assistant's response and metadata
        """
        return await self.chat_service.chat_with_memory(message, user_id, request_time, session_id)

    async def chat_with_memory_stream(
        self, 
        message: str, 
        user_id: str,
        request_time,
        session_id: str = None
    ):
        """
        Process a chat message with memory context and return streaming response
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Yields:
            Streaming response chunks
        """
        async for chunk in self.chat_service.chat_with_memory_stream(message, user_id, request_time, session_id):
            yield chunk