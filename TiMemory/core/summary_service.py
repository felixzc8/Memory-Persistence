from ..config.base import MemoryConfig
from ..llms.openai import OpenAILLM
from ..tidb import TiDB
from ..embedding.openai import OpenAIEmbeddingModel
from ..models.message import Message
from ..session.session_manager import SessionManager
from ..prompts import CONVERSATION_SUMMARY_PROMPT
import logging

class SummaryService:
    """Handles conversation summary generation and management."""
    
    def __init__(self, config: MemoryConfig, llm: OpenAILLM, tidb: TiDB, embedder: OpenAIEmbeddingModel):
        self.config = config
        self.llm = llm
        self.tidb = tidb
        self.embedder = embedder
        self.conversation_summary_prompt = CONVERSATION_SUMMARY_PROMPT
        self.logger = logging.getLogger(__name__)

    def generate_conversation_summary(self, session_id: str, existing_summary: str = None) -> str:
        """Generate summary from existing summary and recent chat messages."""
        
        with self.tidb.SessionLocal() as db:
            recent_messages = db.query(Message).filter(
                Message.session_id == session_id
            ).order_by(Message.created_at.desc()).limit(self.config.message_limit).all()
            
            recent_messages.reverse()
            
            conversation_text = ""
            if existing_summary:
                conversation_text += f"Existing summary: {existing_summary}\n\nRecent conversation:\n"
            else:
                conversation_text += "Conversation to summarize:\n"
            
            for message in recent_messages:
                conversation_text += f"{message.role}: {message.content}\n"
            
            self.logger.info(f"Generating summary with input: {conversation_text}")
            
            response = self.llm.generate_response(
                instructions=self.conversation_summary_prompt,
                input=conversation_text
            ).output_text
            self.logger.info(f"Generated summary response: {response}")
            return response

    def should_generate_summary(self, session_id: str, current_message_count: int, session_manager: SessionManager) -> bool:
        """Check if summary generation is needed based on message threshold."""
        last_summary_at = session_manager.get_last_summary_generated_at(session_id)
        messages_since_summary = current_message_count - last_summary_at
        
        return messages_since_summary >= self.config.summary_threshold

    def update_session_summary(self, session_id: str, summary: str, session_manager: SessionManager) -> None:
        """Update session with new summary content and metadata."""
        current_message_count = session_manager.get_message_count(session_id)
        summary_embedding = self.embedder.embed(summary)
        
        session_manager.update_session_summary(
            session_id, summary, summary_embedding, current_message_count
        )
        
        self.logger.info(f"Updated session {session_id} with new summary at message count {current_message_count}")