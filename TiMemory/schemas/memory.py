from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class MemoryAttributes(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None

class Memory(BaseModel):
    id: str
    user_id: str
    content: str
    memory_attributes: Optional[MemoryAttributes] = None
    
class MemoryResponse(BaseModel):
    memories: List[Memory]
    
class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query for memories")
    user_id: str = Field(..., min_length=1, description="User identifier for memory isolation")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of memories to return")

class MemorySearchResponse(BaseModel):
    memories: List[str] = Field(..., description="List of relevant memories")
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Original search query")