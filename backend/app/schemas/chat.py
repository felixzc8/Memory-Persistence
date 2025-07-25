from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    user_id: str = Field(..., min_length=1, description="User identifier for memory isolation")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation tracking")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    memories_used: List[str] = Field(default=[], description="Relevant memories used for the response")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Response timestamp")


 