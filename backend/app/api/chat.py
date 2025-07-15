from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    MemorySearchRequest, 
    MemorySearchResponse,
    ErrorResponse
)
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    Session,
    SessionSummary,
    SessionListResponse,
    UpdateSessionRequest
)
from app.services.chat_service import chat_service
from app.services.memory_service import memory_service
from app.services.user_service import user_service
from app.services.session_service import session_service
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

# Chat Endpoints
@router.post("/{user_id}/new", response_model=ChatResponse)
async def new_chat_session(user_id: str, request: ChatRequest):
    """
    Create new session and send first message
    """
    try:
        # Validate user_id matches request
        if request.user_id != user_id:
            raise HTTPException(status_code=400, detail="User ID mismatch")
        
        # Check/create user in database
        user = user_service.get_or_create_user(user_id)
        if not user:
            logger.warning(f"Failed to get or create user: {user_id}")
        else:
            user_service.update_user_activity(user_id)
            logger.info(f"User {user_id} authenticated/created successfully")
        
        # Chat service will create new session automatically when session_id is None
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=None  # Force new session creation
        )
        return response
    except Exception as e:
        logger.error(f"Error in new chat session for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{user_id}/{session_id}", response_model=ChatResponse)
async def continue_chat_session(user_id: str, session_id: str, request: ChatRequest):
    """
    Continue conversation in existing session
    """
    try:
        # Validate user_id matches request
        if request.user_id != user_id:
            raise HTTPException(status_code=400, detail="User ID mismatch")
        
        # Validate session exists and belongs to user
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Session does not belong to user")
        
        # Check/create user in database
        user = user_service.get_or_create_user(user_id)
        if not user:
            logger.warning(f"Failed to get or create user: {user_id}")
        else:
            user_service.update_user_activity(user_id)
            logger.info(f"User {user_id} authenticated/created successfully")
        
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=session_id
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat session {session_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Session Management Endpoints
@router.get("/{user_id}/sessions", response_model=SessionListResponse)
async def get_user_sessions(user_id: str, active_only: bool = True):
    """
    Get list of user's sessions
    """
    try:
        sessions = session_service.get_user_sessions(user_id, active_only)
        return SessionListResponse(
            sessions=sessions,
            user_id=user_id,
            total_count=len(sessions)
        )
    except Exception as e:
        logger.error(f"Error getting sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@router.get("/{user_id}/sessions/{session_id}", response_model=Session)
async def get_user_session(user_id: str, session_id: str):
    """
    Get specific session with user validation
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Session does not belong to user")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.put("/{user_id}/sessions/{session_id}")
async def update_user_session(user_id: str, session_id: str, request: UpdateSessionRequest):
    """
    Update session metadata with user validation
    """
    try:
        # Validate session belongs to user
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Session does not belong to user")
        
        success = session_service.update_session(session_id, request)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session")
        return {"message": "Session updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.delete("/{user_id}/sessions/{session_id}")
async def delete_user_session(user_id: str, session_id: str):
    """
    Delete session with user validation
    """
    try:
        # Validate session belongs to user
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Session does not belong to user")
        
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete session")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

# Memory Management Endpoints
@router.post("/{user_id}/memories/search", response_model=MemorySearchResponse)
async def search_user_memories(user_id: str, request: MemorySearchRequest):
    """
    Search through user's memories
    """
    try:
        # Validate user_id matches request
        if request.user_id != user_id:
            raise HTTPException(status_code=400, detail="User ID mismatch")
        
        memories = memory_service.search_memories(
            query=request.query,
            user_id=user_id,
            limit=request.limit
        )
        
        memory_texts = [mem['memory'] for mem in memories]
        
        return MemorySearchResponse(
            memories=memory_texts,
            user_id=user_id,
            query=request.query
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memories for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")

@router.get("/{user_id}/memories/summary")
async def get_user_memory_summary(user_id: str):
    """
    Get a summary of user's conversation history
    """
    try:
        summary = await chat_service.get_conversation_summary(user_id)
        return {"user_id": user_id, "summary": summary}
    except Exception as e:
        logger.error(f"Error getting memory summary for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.delete("/{user_id}/memories")
async def delete_user_memories(user_id: str):
    """
    Delete all memories for the user
    """
    try:
        success = memory_service.delete_memories(user_id)
        if success:
            return {"message": f"Memories deleted for user {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete memories")
    except Exception as e:
        logger.error(f"Error deleting memories for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete memories: {str(e)}")

# Utility Endpoints
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the chat service with TiDB Vector and database status
    """
    try:
        # Check TiDB Vector Store health
        vector_health = memory_service.get_vector_store_health()
        
        # Check database health
        db_health = user_service.get_database_health()
        
        return {
            "status": "healthy",
            "service": "chat",
            "vector_store": vector_health,
            "database": db_health,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Streaming chat endpoints (placeholder for future implementation)
@router.post("/{user_id}/new/stream")
async def new_chat_session_stream(user_id: str, request: ChatRequest):
    """
    Streaming chat endpoint for new sessions (placeholder)
    """
    try:
        # For now, just return a regular response via streaming
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=None
        )
        
        def generate():
            yield f"data: {response.response}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in streaming new chat for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming chat failed: {str(e)}")

@router.post("/{user_id}/{session_id}/stream")
async def continue_chat_session_stream(user_id: str, session_id: str, request: ChatRequest):
    """
    Streaming chat endpoint for existing sessions (placeholder)
    """
    try:
        # Validate session exists and belongs to user
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Session does not belong to user")
        
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=session_id
        )
        
        def generate():
            yield f"data: {response.response}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat session {session_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming chat failed: {str(e)}") 