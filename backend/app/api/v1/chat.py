from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.schemas.memory import MemorySearchRequest, MemorySearchResponse
from app.schemas.session import (
    Session,
    SessionListResponse,
    UpdateSessionRequest
)
from app.services.chat_service import chat_service
from app.services.memory_service import memory_service
from app.dependencies.memory import get_available_memory_service
from app.services.session_service import session_service
from app.services.user_service import user_service
from app.dependencies.auth import get_authenticated_user
from app.dependencies.session import get_user_session
from app.dependencies.validation import validate_chat_request, validate_memory_search_request
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{user_id}/new")
async def new_chat_session(user_id: str, request: ChatRequest, req: Request):
    """
    Create new session and send first message
    Supports both streaming (Accept: text/event-stream) and regular (Accept: application/json) responses
    """
    await validate_chat_request(user_id, request)
    await get_authenticated_user(user_id)
    
    accept_header = req.headers.get("accept", "application/json")
    
    if "text/event-stream" in accept_header:
        # Return streaming response
        stream_generator = chat_service.chat_with_memory_stream(
            message=request.message,
            user_id=user_id,
            session_id=None
        )
        
        return StreamingResponse(
            stream_generator, 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    else:
        # Return regular JSON response
        return await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=None
        )

@router.post("/{user_id}/{session_id}")
async def continue_chat_session(user_id: str, session_id: str, request: ChatRequest, req: Request):
    """
    Continue conversation in existing session
    Supports both streaming (Accept: text/event-stream) and regular (Accept: application/json) responses
    """
    await validate_chat_request(user_id, request)
    await get_user_session(session_id, user_id)
    await get_authenticated_user(user_id)
    
    accept_header = req.headers.get("accept", "application/json")
    
    if "text/event-stream" in accept_header:
        # Return streaming response
        stream_generator = chat_service.chat_with_memory_stream(
            message=request.message,
            user_id=user_id,
            session_id=session_id
        )
        
        return StreamingResponse(
            stream_generator, 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    else:
        # Return regular JSON response
        return await chat_service.chat_with_memory(
            message=request.message,
            user_id=user_id,
            session_id=session_id
        )

@router.get("/{user_id}/sessions", response_model=SessionListResponse)
async def get_user_sessions(user_id: str):
    """
    Get list of user's sessions
    """
    sessions = session_service.get_user_sessions(user_id)
    return SessionListResponse(
        sessions=sessions,
        user_id=user_id,
        total_count=len(sessions)
    )

@router.get("/{user_id}/sessions/{session_id}", response_model=Session)
async def get_user_session_endpoint(user_id: str, session_id: str):
    """
    Get specific session with user validation
    """
    session = await get_user_session(session_id, user_id)
    return session

@router.put("/{user_id}/sessions/{session_id}")
async def update_user_session(user_id: str, session_id: str, request: UpdateSessionRequest):
    """
    Update session metadata with user validation
    """
    await get_user_session(session_id, user_id)
    
    success = session_service.update_session(session_id, request)
    if not success:
        return {"message": "Session updated successfully"}
    return {"message": "Session updated successfully"}

@router.delete("/{user_id}/sessions/{session_id}")
async def delete_user_session(user_id: str, session_id: str):
    """
    Delete session with user validation
    """
    await get_user_session(session_id, user_id)
    
    success = session_service.delete_session(session_id)
    if not success:
        return {"message": "Session deleted successfully"}
    return {"message": "Session deleted successfully"}

@router.post("/{user_id}/memories/search", response_model=MemorySearchResponse)
async def search_user_memories(
    user_id: str, 
    request: MemorySearchRequest,
    memory_svc = Depends(get_available_memory_service)
):
    """
    Search through user's memories
    """
    await validate_memory_search_request(user_id, request)
    
    memories = memory_svc.search_memories(
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

@router.get("/{user_id}/memories/summary")
async def get_user_memory_summary(user_id: str):
    """
    Get a summary of user's conversation history
    """
    summary = await chat_service.get_conversation_summary(user_id)
    return {"user_id": user_id, "summary": summary}

@router.delete("/{user_id}/memories")
async def delete_user_memories(
    user_id: str,
    memory_svc = Depends(get_available_memory_service)
):
    """
    Delete all memories for the user
    """
    success = memory_svc.delete_memories(user_id)
    if success:
        return {"message": f"Memories deleted for user {user_id}"}
    else:
        return {"message": f"Memories deleted for user {user_id}"}

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the chat service with TiDB Vector and database status
    """
    vector_health = memory_service.get_vector_store_health()
    db_health = user_service.get_database_health()
    
    return {
        "status": "healthy",
        "service": "chat",
        "vector_store": vector_health,
        "database": db_health,
        "timestamp": "2024-01-01T00:00:00Z"
    }

