from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    MemorySearchRequest, 
    MemorySearchResponse,
    ErrorResponse
)
from app.services.chat_service import chat_service
from app.services.memory_service import memory_service
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user messages with memory context
    """
    try:
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/memories/search", response_model=MemorySearchResponse)
async def search_memories_endpoint(request: MemorySearchRequest):
    """
    Search through user's memories
    """
    try:
        memories = memory_service.search_memories(
            query=request.query,
            user_id=request.user_id,
            limit=request.limit
        )
        
        memory_texts = [mem['memory'] for mem in memories]
        
        return MemorySearchResponse(
            memories=memory_texts,
            user_id=request.user_id,
            query=request.query
        )
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")

@router.get("/memories/summary/{user_id}")
async def get_memory_summary(user_id: str):
    """
    Get a summary of user's conversation history
    """
    try:
        summary = await chat_service.get_conversation_summary(user_id)
        return {"user_id": user_id, "summary": summary}
    except Exception as e:
        logger.error(f"Error getting memory summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.delete("/memories/{user_id}")
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
        logger.error(f"Error deleting memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete memories: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the chat service with TiDB Vector status
    """
    try:
        # Check TiDB Vector Store health
        vector_health = memory_service.get_vector_store_health()
        
        return {
            "status": "healthy",
            "service": "chat",
            "vector_store": vector_health,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Optional: Add a streaming chat endpoint for real-time responses
@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint (placeholder for future implementation)
    """
    # This would implement streaming responses for better UX
    # For now, just return a regular response
    try:
        response = await chat_service.chat_with_memory(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        def generate():
            # In a real implementation, you'd stream the response word by word
            yield f"data: {response.response}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming chat failed: {str(e)}") 