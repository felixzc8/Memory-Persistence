from .llms.openai import OpenAILLM
from .embedding.openai import OpenAIEmbeddingModel
from .tidb import TiDB
from .session.session_manager import SessionManager
from .knowledge_graph_client import KnowledgeGraphClient
from typing import List, Dict
from .schemas.memory import Memory, MemoryResponse
from .config.base import MemoryConfig
from TiMemory.tasks.worker_tasks import process_memories
from .core import MemoryProcessor, SummaryProcessor, TopicProcessor

import logging

class TiMemory:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self._setup_services()
        
    def _setup_services(self):
        """Initialize all services and their dependencies."""
        self.tidb = TiDB(self.config)
        self.embedder = OpenAIEmbeddingModel(self.config)
        self.llm = OpenAILLM(self.config)
        
        self.session_manager = SessionManager(
            db_session_factory=self.tidb.SessionLocal
        )
        
        self.memory_processor = MemoryProcessor(
            config=self.config,
            llm=self.llm
            llm=self.llm
        )
        
        self.summary_processor = SummaryProcessor(
        self.summary_processor = SummaryProcessor(
            config=self.config,
            llm=self.llm
            llm=self.llm
        )
        
        self.topic_processor = TopicProcessor(
        self.topic_processor = TopicProcessor(
            config=self.config,
            llm=self.llm
        )
        
        
        self.knowledge_graph_client = KnowledgeGraphClient(
            config=self.config
        )


    def _should_process_memories(self, session_id: str) -> bool:
        """Check if there are new messages to process."""
        last_processed_at = self.session_manager.get_last_memory_processed_at(session_id)
        current_message_count = self.session_manager.get_message_count(session_id)
        
        if current_message_count <= last_processed_at:
            self.logger.info(f"No new messages to process for session {session_id} (current: {current_message_count}, last processed: {last_processed_at})")
            return False
        
        return True

    def _get_unprocessed_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get messages from last processed point to current."""
        last_processed_at = self.session_manager.get_last_memory_processed_at(session_id)
        
        return self.session_manager.get_messages_since_count(
            session_id, last_processed_at
        )

    def _trigger_memory_processing(self, messages: List[Dict[str, str]], user_id: str, session_id: str) -> None:
        """Queue memory processing for background execution."""
        from TiMemory.tasks.worker_tasks import process_memories
        
        task = process_memories.delay(messages, user_id, session_id)
        self.logger.info(f"Queued background memory processing task {task.id} for user {user_id}")


    def _check_summary_needed(self, session_id: str) -> bool:
        """Check if summary generation is needed based on max_context_message_count."""
        current_message_count = self.session_manager.get_message_count(session_id)
        last_summary_at = self.session_manager.get_last_summary_generated_at(session_id)
        messages_since_summary = current_message_count - last_summary_at
        return messages_since_summary >= self.config.max_context_message_count

    def _generate_and_update_summary(self, session_id: str) -> None:
        """Queue summary processing for background execution."""
        from TiMemory.tasks.worker_tasks import process_summary
        
        task = process_summary.delay(session_id)
        self.logger.info(f"Queued background summary processing task {task.id} for session {session_id}")

    def _build_context(self, message: str, user_id: str, session_id: str) -> tuple[str, List[Memory]]:
        """Build complete context including system prompt, memories, summary, and session context."""
        from .prompts import SYSTEM_PROMPT
        
        summary = self.session_manager.get_session_summary(session_id)
        session_context = self.session_manager.get_session_message_context(session_id)
        
        memories = self._get_memory_context(message, user_id)
        
        context = SYSTEM_PROMPT
        context += f"\n MEMORIES: {memories}"
        context += f"\n SUMMARY: {summary}"
        context += f"\n SESSION CONTEXT: {session_context}"
        
        return context, memories

    def _get_memory_context(self, message: str, user_id: str) -> List[Memory]:
        """Get relevant memories for the current message."""
        return self.search(
            query=message, 
            user_id=user_id, 
            limit=self.config.memory_search_limit
        )

    def search(self, query: str, user_id: str, limit: int = 10) -> List[Memory]:
        """
        Search for memories based on a query string.
        Returns a list of Memory objects.
        """
        embedding = self.embedder.embed(query)
        results = self.tidb.search_memories(embedding, user_id, limit=limit)
        return results.memories
        embedding = self.embedder.embed(query)
        results = self.tidb.search_memories(embedding, user_id, limit=limit)
        return results.memories

    def get_all_memories(self, user_id: str) -> MemoryResponse:
        """        
        Get all memories for a user.
        Returns a MemoryResponse containing a list of Memory objects.
        """
        return self.tidb.get_memories_by_user(user_id)

        return self.tidb.get_memories_by_user(user_id)


    def delete_all(self, user_id: str):
        """
        Delete all memories for a user.
        """
        self.tidb.delete_all_memories(user_id=user_id)
        self.tidb.delete_all_memories(user_id=user_id)

    def check_and_process_topic_change(self, user_id: str, session_id: str) -> bool:
        """
        Check for topic changes and trigger memory/summary processing if needed.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            bool: True if topic change was detected and processing triggered
        """
        try:
            if not self._should_process_memories(session_id):
                return False
            
            unprocessed_messages = self._get_unprocessed_messages(session_id)
            
            if len(unprocessed_messages) < 2:
                self.logger.info(f"Insufficient messages for topic change detection: {len(unprocessed_messages)} (need at least 2)")
                return False
            
            self.logger.info(f"Checking {len(unprocessed_messages)} unprocessed messages for topic change in session {session_id}")
            topic_changed = self.topic_processor.detect_topic_change(unprocessed_messages)
            
            if topic_changed:
                self.logger.info(f"Topic change detected! Processing {len(unprocessed_messages)} messages for memory extraction in session {session_id}")
                
                self._trigger_memory_processing(unprocessed_messages, user_id, session_id)
                
                if self._check_summary_needed(session_id):
                    self._generate_and_update_summary(session_id)
                
                return True
            else:
                self.logger.info(f"No topic change detected for session {session_id}, skipping memory processing")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in topic change processing for session {session_id}: {e}")
            return False

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
        try:
            from datetime import datetime, timezone
            
            context, memories_used = self._build_context(message, user_id, session_id)
            
            user_message = [{"role": "user", "content": message}]
            
            self.logger.debug(f"LLM call context - Instructions: {context}, Input: {user_message}")
            
            response = self.llm.generate_response(
                instructions=context,
                input=user_message
            )
            
            assistant_response = response.output_text
            assistant_timestamp = datetime.now(timezone.utc)
            
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", assistant_response, assistant_timestamp)
            
            self.check_and_process_topic_change(user_id, session_id)
            
            return {
                "response": assistant_response,
                "user_id": user_id,
                "session_id": session_id,
                "memories_used": [mem.content for mem in memories_used],
                "timestamp": assistant_timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat_with_memory for user {user_id}: {e}")
            raise

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
        try:
            from datetime import datetime, timezone
            import openai
            
            context, memories_used = self._build_context(message, user_id, session_id)
            
            self.logger.info(f"LLM streaming call context - Instructions: {context}, Input: {message}")
            
            client = openai.OpenAI(api_key=self.config.openai_api_key)
            
            stream = client.chat.completions.create(
                model=self.config.model_choice,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            assistant_timestamp = datetime.now(timezone.utc)
            
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", full_response, assistant_timestamp)
            
            self.check_and_process_topic_change(user_id, session_id)
            
            yield {
                "user_id": user_id,
                "session_id": session_id,
                "memories_used": memories_used,
                "timestamp": assistant_timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat_with_memory_stream for user {user_id}: {e}")
            raise
