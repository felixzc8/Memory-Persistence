from ..config.base import MemoryConfig
from ..llms.openai import OpenAILLM
from ..prompts import CONVERSATION_SUMMARY_PROMPT
from typing import List, Dict
import logging

class SummaryProcessor:
    """Handles conversation summary generation and management."""
    
    def __init__(self, config: MemoryConfig, llm: OpenAILLM):
        self.config = config
        self.llm = llm
        self.conversation_summary_prompt = CONVERSATION_SUMMARY_PROMPT
        self.logger = logging.getLogger(__name__)

    def generate_conversation_summary(self, recent_messages: List[Dict[str, str]], existing_summary: str = None) -> str:
        """Generate summary from existing summary and recent chat messages."""
        
        conversation_text = ""
        if existing_summary:
            conversation_text += f"Existing summary: {existing_summary}\n\nRecent conversation:\n"
        else:
            conversation_text += "Conversation to summarize:\n"
        
        for message in recent_messages:
            conversation_text += f"{message['role']}: {message['content']}\n"
        
        self.logger.info(f"Generating summary with input: {conversation_text}")
        
        response = self.llm.generate_response(
            instructions=self.conversation_summary_prompt,
            input=conversation_text
        ).output_text
        self.logger.info(f"Generated summary response: {response}")
        return response

    def should_generate_summary(self, current_message_count: int, last_summary_at: int) -> bool:
        """Check if summary generation is needed."""
        # Summary threshold logic removed - external caller determines when to generate summary
        return True