from typing import List, Dict
from ..config.base import MemoryConfig
from ..llms.openai import OpenAILLM
from ..schemas.memory import TopicChangedResponse
from ..prompts import TOPIC_CHANGE_DETECTION_PROMPT
import logging

class TopicProcessor:
    """Handles topic change detection and coordinates memory/summary processing."""
    
    def __init__(self, config: MemoryConfig, llm: OpenAILLM):
        self.config = config
        self.llm = llm
        self.topic_change_detection_prompt = TOPIC_CHANGE_DETECTION_PROMPT
        self.logger = logging.getLogger(__name__)


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

