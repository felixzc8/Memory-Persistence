from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

class MemoryAttributes(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None

class ExtractionMemoryAttributes(BaseModel):
    type: str
    
class Memory(BaseModel):
    id: str
    user_id: str
    content: str
    memory_attributes: MemoryAttributes
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MemoryExtractionItem(BaseModel):
    content: str
    memory_attributes: ExtractionMemoryAttributes

class MemoryExtractionResponse(BaseModel):
    memories: List[MemoryExtractionItem]

class MemoryConsolidationItem(BaseModel):
    id: str
    content: str
    memory_attributes: MemoryAttributes

class MemoryConsolidationResponse(BaseModel):
    memories: List[MemoryConsolidationItem]
    
class MemoryResponse(BaseModel):
    memories: List[Memory]
    
class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query for memories")
    user_id: str = Field(..., min_length=1, description="User identifier for memory isolation")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of memories to return")

class MemorySearchResponse(BaseModel):
    memories: List[str] = Field(..., description="List of relevant memories")
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Original search query")