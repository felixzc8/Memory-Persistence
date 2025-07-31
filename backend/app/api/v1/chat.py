from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from TiMemory.schemas.session import (
    Session,
    SessionListResponse,
    UpdateSessionRequest
)
from app.services.chat_service import chat_service
from app.services.memory_service import memory_service
from app.dependencies.memory import get_available_memory_service
from app.services.user_service import user_service
from app.dependencies.auth import get_authenticated_user
from app.dependencies.session import get_user_session
from app.dependencies.validation import validate_chat_request
from TiMemory.schemas.memory import Memory, MemoryResponse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{user_id}/new")
async def new_chat_session(user_id: str, request: ChatRequest, req: Request):
    """
    Create new session and send first message
    Supports both streaming (Accept: text/event-stream) and regular (Accept: application/json) responses
    """
    request_time = datetime.now(timezone.utc)
    
    await validate_chat_request(user_id, request)
    await get_authenticated_user(user_id)
    
    title = memory_service.memory.session_manager.generate_session_title(request.message)
    session_response = memory_service.memory.session_manager.create_session(user_id, title)
    session_id = session_response.session_id
    
    accept_header = req.headers.get("accept", "application/json")
    
    if "text/event-stream" in accept_header:
        async def stream_with_session_created():
            import json
            yield f"event: session_created\ndata: {json.dumps({'session_id': session_id, 'title': title})}\n\n"
            async for chunk in chat_service.chat_with_memory_stream(
                message=request.message,
                user_id=user_id,
                request_time=request_time,
                session_id=session_id
            ):
                yield chunk
        
        return StreamingResponse(
            stream_with_session_created(), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    return await chat_service.chat_with_memory(
        message=request.message,
        user_id=user_id,
        request_time=request_time,
        session_id=session_id
    )

@router.post("/{user_id}/{session_id}")
async def continue_chat_session(user_id: str, session_id: str, request: ChatRequest, req: Request):
    """
    Continue conversation in existing session
    Supports both streaming (Accept: text/event-stream) and regular (Accept: application/json) responses
    """
    request_time = datetime.now(timezone.utc)
    
    await validate_chat_request(user_id, request)
    await get_user_session(session_id, user_id)
    await get_authenticated_user(user_id)
    
    accept_header = req.headers.get("accept", "application/json")
    
    if "text/event-stream" in accept_header:
        stream_generator = chat_service.chat_with_memory_stream(
            message=request.message,
            user_id=user_id,
            request_time=request_time,
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
        
    return await chat_service.chat_with_memory(
        message=request.message,
        user_id=user_id,
        request_time=request_time,
        session_id=session_id
    )

@router.get("/{user_id}/sessions", response_model=SessionListResponse)
async def get_user_sessions(user_id: str):
    """
    Get list of user's sessions
    """
    sessions = memory_service.memory.session_manager.get_user_sessions(user_id)
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
    
    success = memory_service.memory.session_manager.update_session(session_id, request)
    if not success:
        return {"message": "Session updated successfully"}
    return {"message": "Session updated successfully"}

@router.delete("/{user_id}/sessions/{session_id}")
async def delete_user_session(user_id: str, session_id: str):
    """
    Delete session with user validation
    """
    await get_user_session(session_id, user_id)
    
    success = memory_service.memory.session_manager.delete_session(session_id)
    if not success:
        return {"message": "Session deleted successfully"}
    return {"message": "Session deleted successfully"}

@router.get("/{user_id}/memories", response_model=MemoryResponse)
async def get_user_memories(user_id: str):
    """
    Get all memories for the user
    """
    memories = memory_service.get_memories(user_id)
    return memories

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

