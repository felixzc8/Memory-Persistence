from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Memory(BaseModel):
    id: int
    type: str
    content: str
    status: Optional[str]
    created_at: Optional[datetime]
    
class MemoryResponse(BaseModel):
    facts: List[Memory]