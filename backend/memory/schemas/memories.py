from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MemoryAttributes(BaseModel):
    type: Optional[str] = None
    status: Optional[str] = None

class Memory(BaseModel):
    id: str
    vector: Optional[List[float]] = None
    user_id: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    memory_attributes: Optional[MemoryAttributes] = None
    
class MemoryResponse(BaseModel):
    memories: List[Memory]