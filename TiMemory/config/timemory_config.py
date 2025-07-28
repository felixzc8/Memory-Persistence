import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from .base import MemoryConfig

def load_timemory_env():
    """Load TiMemory-specific .env file if it exists"""
    timemory_dir = Path(__file__).parent.parent
    env_path = timemory_dir / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False

class TiMemoryConfig:
    """TiMemory-specific configuration wrapper that adds knowledge graph settings"""
    
    def __init__(self, base_config: MemoryConfig):
        load_timemory_env()
        self._base_config = base_config
    
    @property
    def knowledge_graph_url(self) -> Optional[str]:
        """Get knowledge graph URL from TiMemory environment"""
        return os.getenv("KNOWLEDGE_GRAPH_URL")
    
    
    def __getattr__(self, name):
        """Delegate all other attributes to the base config"""
        return getattr(self._base_config, name)