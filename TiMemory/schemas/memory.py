from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    
class TopicChangedResponse(BaseModel):
    topic_changed: bool