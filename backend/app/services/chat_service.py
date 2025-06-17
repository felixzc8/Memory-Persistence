from openai import OpenAI
from typing import List, Dict, Tuple
from app.config import settings
from app.services.memory_service import memory_service
from app.schemas.chat import ChatMessage, ChatResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with OpenAI and memory integration"""
    
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def chat_with_memory(
        self, 
        message: str, 
        user_id: str = "default_user",
        session_id: str = None
    ) -> ChatResponse:
        """
        Process a chat message with memory context
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            session_id: Optional session identifier
            
        Returns:
            ChatResponse with assistant's response and metadata
        """
        try:
            # Get relevant memories
            memories = memory_service.search_memories(
                query=message, 
                user_id=user_id, 
                limit=settings.memory_search_limit
            )
            
            # Format memory context
            memories_context = self._format_memory_context(memories)
            memories_used = [mem['memory'] for mem in memories]
            
            # Create system prompt with memory context
            system_prompt = self._create_system_prompt(memories_context)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=settings.model_choice,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # Save conversation to memory
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response}
            ]
            
            memory_service.add_memory(conversation_messages, user_id)
            
            return ChatResponse(
                response=assistant_response,
                user_id=user_id,
                session_id=session_id,
                memories_used=memories_used,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory for user {user_id}: {e}")
            raise
    
    def _format_memory_context(self, memories: List[Dict]) -> str:
        """Format memories into a context string"""
        if not memories:
            return "No relevant memories found."
        
        memories_str = "\n".join(f"- {entry['memory']}" for entry in memories)
        return f"User memories:\n{memories_str}"
    
    def _create_system_prompt(self, memories_context: str) -> str:
        """Create system prompt with memory context"""
        return f"""You are Homi, a helpful and friendly assistant with persistent memory. 
        
Answer the user's question based on the conversation context and their memories.
Be conversational, helpful, and remember to use the provided memories when relevant.

{memories_context}

Guidelines:
- Be natural and conversational
- Use memories when they're relevant to the current conversation
- If no memories are relevant, respond normally
- Keep responses concise but informative
- Maintain a friendly and helpful tone"""

    async def get_conversation_summary(self, user_id: str, limit: int = 10) -> str:
        """Get a summary of recent conversations for a user"""
        try:
            memories = memory_service.search_memories(
                query="conversation summary",
                user_id=user_id,
                limit=limit
            )
            
            if not memories:
                return "No conversation history found."
            
            # Create a summary prompt
            memories_text = "\n".join([mem['memory'] for mem in memories])
            
            messages = [
                {
                    "role": "system", 
                    "content": "Summarize the following conversation history in a concise and helpful way:"
                },
                {
                    "role": "user", 
                    "content": memories_text
                }
            ]
            
            response = self.client.chat.completions.create(
                model=settings.model_choice,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting conversation summary for user {user_id}: {e}")
            return "Unable to generate conversation summary."

# Singleton instance
chat_service = ChatService() 