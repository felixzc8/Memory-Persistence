from typing import List, Dict
from ..config.base import MemoryConfig
from ..llms.openai import OpenAILLM
from ..session.session_manager import SessionManager
from .memory_processor import MemoryProcessor
from .summary_service import SummaryService
from ..schemas.memory import TopicChangedResponse
from ..prompts import TOPIC_CHANGE_DETECTION_PROMPT
import logging

class TopicDetector:
    """Handles topic change detection and coordinates memory/summary processing."""
    
    def __init__(self, 
                 config: MemoryConfig, 
                 llm: OpenAILLM, 
                 session_manager: SessionManager,
                 memory_processor: MemoryProcessor, 
                 summary_service: SummaryService):
        self.config = config
        self.llm = llm
        self.session_manager = session_manager
        self.memory_processor = memory_processor
        self.summary_service = summary_service
        self.topic_change_detection_prompt = TOPIC_CHANGE_DETECTION_PROMPT
        self.logger = logging.getLogger(__name__)

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
            # Check if we should process memories
            if not self._should_process_memories(session_id):
                return False
            
            # Get unprocessed messages
            unprocessed_messages = self._get_unprocessed_messages(session_id)
            
            if len(unprocessed_messages) < 2:
                self.logger.info(f"Insufficient messages for topic change detection: {len(unprocessed_messages)} (need at least 2)")
                return False
            
            # Check for topic change using LLM
            self.logger.info(f"Checking {len(unprocessed_messages)} unprocessed messages for topic change in session {session_id}")
            topic_changed = self.detect_topic_change(unprocessed_messages)
            
            if topic_changed:
                self.logger.info(f"Topic change detected! Processing {len(unprocessed_messages)} messages for memory extraction in session {session_id}")
                
                # Trigger memory processing
                self._trigger_memory_processing(unprocessed_messages, user_id, session_id)
                
                # Update last processed message count
                current_message_count = self.session_manager.get_message_count(session_id)
                self.session_manager.update_last_memory_processed_at(session_id, current_message_count)
                
                # Check if summary generation is needed
                if self._check_summary_threshold(session_id):
                    self._generate_and_update_summary(session_id)
                
                return True
            else:
                self.logger.info(f"No topic change detected for session {session_id}, skipping memory processing")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in topic change processing for session {session_id}: {e}")
            return False

    def detect_topic_change(self, messages: List[Dict[str, str]]) -> bool:
        """
        Analyze a sequence of messages to detect if there has been a topic change.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            bool: True if topic change detected, False otherwise
        """
        if not messages or len(messages) < 2:
            return False
            
        try:
            self.logger.info(f"Calling LLM to analyze {len(messages)} messages for topic change detection")
            
            response = self.llm.generate_parsed_response(
                instructions=self.topic_change_detection_prompt,
                input=messages,
                text_format=TopicChangedResponse
            ).output_parsed
            
            topic_changed = response.topic_changed
            self.logger.info(f"LLM topic change detection returned: {topic_changed}")
            
            return topic_changed
            
        except Exception as e:
            self.logger.error(f"Error in topic change detection: {e}")
            return False

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
        """Process memories for the unprocessed message segment."""
        self.memory_processor.process_memories(messages, user_id, session_id)

    def _check_summary_threshold(self, session_id: str) -> bool:
        """Check if summary generation is needed based on message threshold."""
        current_message_count = self.session_manager.get_message_count(session_id)
        return self.summary_service.should_generate_summary(session_id, current_message_count, self.session_manager)

    def _generate_and_update_summary(self, session_id: str) -> None:
        """Generate new conversation summary and update session."""
        current_summary = self.session_manager.get_session_summary(session_id)
        new_summary = self.summary_service.generate_conversation_summary(session_id, current_summary)
        self.summary_service.update_session_summary(session_id, new_summary, self.session_manager)
        
        self.logger.info(f"Generated and updated summary for session {session_id}")