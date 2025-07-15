from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class SessionMessage(BaseModel):
    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp")

class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User identifier")
    title: Optional[str] = Field(None, max_length=100, description="Optional session title")

class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Session title")
    created_at: datetime = Field(..., description="Session creation timestamp")

class Session(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Session title")
    messages: List[SessionMessage] = Field(default=[], description="Session messages")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Whether session is active")
    message_count: int = Field(default=0, description="Total message count in session")

class SessionSummary(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Session title")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Total message count in session")
    is_active: bool = Field(default=True, description="Whether session is active")

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=100, description="New session title")
    is_active: Optional[bool] = Field(None, description="Session active status")

class SessionListResponse(BaseModel):
    sessions: List[SessionSummary] = Field(..., description="List of user sessions")
    user_id: str = Field(..., description="User identifier")
    total_count: int = Field(..., description="Total number of sessions")