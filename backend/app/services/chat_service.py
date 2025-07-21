from openai import OpenAI
from typing import List, Dict, Tuple, AsyncGenerator
from app.core.config import settings
from app.services.memory_service import memory_service
from app.services.session_service import session_service
from app.schemas.chat import ChatMessage, ChatResponse
import logging
from datetime import datetime
import json

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
    
    async def chat_with_memory_stream(
        self, 
        message: str, 
        user_id: str,
        session_id: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat message with memory context and session history (streaming version)
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            session_id: Optional session identifier for conversation context
            
        Yields:
            SSE-formatted strings with streaming response chunks
        """
        try:
            if not session_id:
                title = session_service.generate_session_title(message)
                session_response = session_service.create_session(user_id, title)
                session_id = session_response.session_id
                logger.info(f"Created new session {session_id} for user {user_id}")
                
                yield f"event: session_created\ndata: {json.dumps({'session_id': session_id, 'title': title})}\n\n"
            
            session_context = session_service.get_session_context(session_id, limit=20)
            
            memories_context = memory_service.get_memory_context(
                query=message, 
                user_id=user_id, 
                limit=5
            )
            
            memories = memory_service.search_memories(
                query=message, 
                user_id=user_id, 
                limit=5
            )
            memories_used = [mem.content for mem in memories]
            
            yield f"event: memories_loaded\ndata: {json.dumps({'count': len(memories_used)})}\n\n"
            
            system_prompt = self.create_system_prompt(memories_context)
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(session_context)
            messages.append({"role": "user", "content": message})
            
            session_service.add_message_to_session(session_id, "user", message)
            full_response = ""
            
            stream = self.client.chat.completions.create(
                model=settings.model_choice,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"event: content\ndata: {json.dumps({'content': content})}\n\n"
            
            session_service.add_message_to_session(session_id, "assistant", full_response)
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": full_response}
            ]
            
            memory_service.add_memory(conversation_messages, user_id)
            
            completion_data = {
                'session_id': session_id,
                'memories_used': memories_used,
                'timestamp': datetime.utcnow().isoformat()
            }
            yield f"event: complete\ndata: {json.dumps(completion_data)}\n\n"
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory_stream for user {user_id}: {e}")
            error_data = {'error': str(e)}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    async def chat_with_memory(
        self, 
        message: str, 
        user_id: str,
        session_id: str = None
    ) -> ChatResponse:
        """
        Process a chat message with memory context and session history
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            session_id: Optional session identifier for conversation context
            
        Returns:
            ChatResponse with assistant's response and metadata
        """
        try:
            if not session_id:
                title = session_service.generate_session_title(message)
                session_response = session_service.create_session(user_id, title)
                session_id = session_response.session_id
                logger.info(f"Created new session {session_id} for user {user_id}")
            
            session_context = session_service.get_session_context(session_id, limit=15)
            
            memories_context = memory_service.get_memory_context(
                query=message, 
                user_id=user_id, 
                limit=5
            )
            
            memories = memory_service.search_memories(
                query=message, 
                user_id=user_id, 
                limit=5
            )
            memories_used = [mem.content for mem in memories]
            
            system_prompt = self.create_system_prompt(memories_context)
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(session_context)
            messages.append({"role": "user", "content": message})
            response = self.client.chat.completions.create(
                model=settings.model_choice,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            session_service.add_message_to_session(session_id, "user", message)
            session_service.add_message_to_session(session_id, "assistant", assistant_response)
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
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting conversation summary for user {user_id}: {e}")
            return "Unable to generate conversation summary."
        
    def create_system_prompt(self, memories_context: str) -> str:
        """Create system prompt with memory context"""
        return f"""You are a helpful and friendly assistant with persistent memory and conversation history.

        You have access to both:
        1. Recent conversation history in this session
        2. Long-term memories from past conversations

        Answer the user's question based on the conversation context and their memories.
        Be conversational, helpful, and remember to use the provided memories when relevant.

        {memories_context}

        Guidelines:
        - Be natural and conversational
        - Use the conversation history to maintain context within this session
        - Use long-term memories when they're relevant to the current conversation
        - If no memories are relevant, respond normally based on the conversation
        - Keep responses concise but informative"""


chat_service = ChatService() 