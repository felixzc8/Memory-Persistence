from pydantic import BaseModel, Field
from datetime import datetime


class SummaryResponse(BaseModel):
    id: str = Field(..., description="Unique summary identifier")
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., description="Summary content")
    message_count_at_creation: int = Field(..., description="Total messages when summary was created")
    created_at: datetime = Field(..., description="Summary creation timestamp")

class CreateSummaryRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., min_length=1, description="Summary content")
    message_count_at_creation: int = Field(..., ge=0, description="Total messages when summary was created")