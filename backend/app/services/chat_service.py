from typing import AsyncGenerator
from app.services.memory_service import memory_service
from app.schemas.chat import ChatResponse
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions using TiMemory"""
    
    def __init__(self):
        logger.info("Chat service initialized with TiMemory")
    
    async def chat_with_memory(
        self, 
        message: str, 
        user_id: str,
        request_time: datetime,
        session_id: str = None
    ) -> ChatResponse:
        """
        Process a chat message with memory context and session history (non-streaming version)
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Returns:
            ChatResponse with assistant's response and metadata including memories
        """
        try:
            response_data = await memory_service.memory.chat_with_memory(message, user_id, request_time, session_id)
            
            # Topic change detection and memory processing now handled within chat_with_memory
            
            return ChatResponse(
                response=response_data["response"],
                user_id=response_data["user_id"],
                session_id=response_data["session_id"],
                memories_used=response_data["memories_used"],
                timestamp=response_data["timestamp"]
            )
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory for user {user_id}: {e}")
            raise
    
    async def chat_with_memory_stream(
        self, 
        message: str, 
        user_id: str,
        request_time: datetime,
        session_id: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a chat message with memory context and session history (streaming version)
        
        Args:
            message: User's message
            user_id: Unique identifier for the user
            request_time: Timestamp of the request
            session_id: Optional session identifier for conversation context
            
        Yields:
            SSE-formatted strings with streaming response chunks
        """
        try:
            stream_generator = memory_service.memory.chat_with_memory_stream(message, user_id, request_time, session_id)
            
            async for content in stream_generator:
                if isinstance(content, str):
                    yield f"event: content\ndata: {json.dumps({'content': content})}\n\n"
                elif isinstance(content, dict):
                    # Topic change detection and memory processing now handled within chat_with_memory_stream
                    yield f"event: complete\ndata: {json.dumps({'session_id': content.get('session_id'), 'memories': content.get('memories'), 'status': 'completed'})}\n\n"
                    return
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory_stream for user {user_id}: {e}")
            error_data = {'error': str(e)}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

chat_service = ChatService()