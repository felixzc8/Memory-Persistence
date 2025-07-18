from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Memory(BaseModel):
    id: str
    type: str
    content: str
    status: Optional[str]
    
class MemoryResponse(BaseModel):
    memories: List[Memory]