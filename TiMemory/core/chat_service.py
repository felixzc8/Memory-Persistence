from typing import Dict, List, AsyncGenerator
from ..config.base import MemoryConfig
from ..llms.openai import OpenAILLM
from .memory_processor import MemoryProcessor
from ..session.session_manager import SessionManager
from ..schemas.memory import Memory
import logging

class ChatService:
    """Handles chat functionality with memory context."""
    
    def __init__(self, config: MemoryConfig, llm: OpenAILLM, memory_processor: MemoryProcessor, session_manager: SessionManager, topic_detector=None):
        self.config = config
        self.llm = llm
        self.memory_processor = memory_processor
        self.session_manager = session_manager
        self.topic_detector = topic_detector
        self.logger = logging.getLogger(__name__)

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
            from ..prompts import SYSTEM_PROMPT
            from datetime import datetime, timezone
            
            # Build context from session and memories
            context = self._build_context(message, user_id, session_id)
            memories_used = self._get_memory_context(message, user_id)
            
            user_message = [{"role": "user", "content": message}]
            
            self.logger.debug(f"LLM call context - Instructions: {context}, Input: {user_message}")
            
            response = self.llm.generate_response(
                instructions=context,
                input=user_message
            )
            
            assistant_response = response.output_text
            assistant_timestamp = datetime.now(timezone.utc)
            
            # Store the conversation
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", assistant_response, assistant_timestamp)
            
            # Check for topic change and process memories if needed
            if self.topic_detector:
                self.topic_detector.check_and_process_topic_change(user_id, session_id)
            
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
    ) -> AsyncGenerator:
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
            
            # Build context from session and memories
            context = self._build_context(message, user_id, session_id)
            memories_used = self._get_memory_context(message, user_id)
            
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
            
            # Store the conversation
            self.session_manager.add_message_to_session(session_id, "user", message, request_time)
            self.session_manager.add_message_to_session(session_id, "assistant", full_response, assistant_timestamp)
            
            # Check for topic change and process memories if needed
            if self.topic_detector:
                self.topic_detector.check_and_process_topic_change(user_id, session_id)
            
            # Yield final metadata
            yield {
                "user_id": user_id,
                "session_id": session_id,
                "memories_used": memories_used,
                "timestamp": assistant_timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat_with_memory_stream for user {user_id}: {e}")
            raise

    def _build_context(self, message: str, user_id: str, session_id: str) -> str:
        """Build complete context including system prompt, memories, summary, and session context."""
        from ..prompts import SYSTEM_PROMPT
        
        summary = self.session_manager.get_session_summary(session_id)
        session_context = self.session_manager.get_session_message_context(
            session_id, 
            self.config.message_limit
        )
        
        memories = self._get_memory_context(message, user_id)
        
        context = SYSTEM_PROMPT
        context += f"\n MEMORIES: {memories}"
        context += f"\n SUMMARY: {summary}"
        context += f"\n SESSION CONTEXT: {session_context}"
        
        return context

    def _get_memory_context(self, message: str, user_id: str) -> List[Memory]:
        """Get relevant memories for the current message."""
        return self.memory_processor.search(
            query=message, 
            user_id=user_id, 
            limit=self.config.memory_search_limit
        )