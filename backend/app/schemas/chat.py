from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation tracking")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    memories_used: List[str] = Field(default=[], description="Relevant memories used for the response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query for memories")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of memories to return")

class MemorySearchResponse(BaseModel):
    memories: List[str] = Field(..., description="List of relevant memories")
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Original search query")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp") 