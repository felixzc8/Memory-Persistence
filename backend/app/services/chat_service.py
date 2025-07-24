from openai import OpenAI
from typing import AsyncGenerator
from app.core.config import settings
from app.services.memory_service import memory_service
from app.schemas.chat import ChatResponse
from TiMemory.prompts import SYSTEM_PROMPT
import logging
from datetime import datetime, timezone
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
            summary, session_context = memory_service.memory.session_manager.get_session_context_with_summary(
                session_id, 
                memory_service.memory.message_limit
            )

            memories_context = memory_service.get_memory_context(
                query=message, 
                user_id=user_id, 
                limit=settings.memory_search_limit
            )
            
            instructions = SYSTEM_PROMPT + f"\n MEMORIES: {memories_context}"
            instructions += f"\n SUMMARY: {summary}"
            instructions += f"\n SESSION CONTEXT: {session_context}"
            user_message = [{"role": "user", "content": message}]
            
            stream = self.client.responses.create(
                model=settings.model_choice,
                instructions=instructions,
                input=user_message,
                stream=True
            )
            
            full_response = ""
            
            for event in stream:
                if event.type == "response.output_text.delta":
                    content = event.delta
                    full_response += content
                    yield f"event: content\ndata: {json.dumps({'content': content})}\n\n"
                elif event.type == "response.completed":
                    yield f"event: complete\ndata: {json.dumps({'status': 'completed'})}\n\n"
                elif event.type == "error":
                    logger.error(f"Streaming error: {event}")
                    yield f"event: error\ndata: {json.dumps({'error': str(event)})}\n\n"
            
            
            memory_service.memory.session_manager.add_message_to_session(session_id, "user", message)
            memory_service.memory.session_manager.add_message_to_session(session_id, "assistant", full_response)
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": full_response}
            ]
            
            await memory_service.add_memory(conversation_messages, user_id, session_id)
            
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
            
            summary, session_context = memory_service.memory.session_manager.get_session_context_with_summary(
                session_id, 
                memory_service.memory.message_limit
            )
            
            memories_context = memory_service.get_memory_context(
                query=message, 
                user_id=user_id, 
                limit=settings.memory_search_limit
            )

            memories = memory_service.search_memories(
                query=message, 
                user_id=user_id, 
                limit=settings.memory_search_limit
            )
            memories_used = [mem.content for mem in memories]
            
            instructions = SYSTEM_PROMPT + f"\n MEMORIES: {memories_context}"
            instructions += f"\n SUMMARY: {summary}"
            instructions += f"\n SESSION CONTEXT: {session_context}"
            user_message = [{"role": "user", "content": message}]
            
            response = self.client.responses.create(
                model=settings.model_choice,
                instructions=instructions,
                messages=user_message
            )
            
            assistant_response = response.choices[0].message.content
            
            memory_service.memory.session_manager.add_message_to_session(session_id, "user", message)
            memory_service.memory.session_manager.add_message_to_session(session_id, "assistant", assistant_response)
            conversation_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_response}
            ]
            
            await memory_service.add_memory(conversation_messages, user_id, session_id)
            
            return ChatResponse(
                response=assistant_response,
                user_id=user_id,
                session_id=session_id,
                memories_used=memories_used,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory for user {user_id}: {e}")
            raise

chat_service = ChatService()