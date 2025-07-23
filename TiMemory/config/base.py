from abc import ABC, abstractmethod
from typing import Optional

class MemoryConfig(ABC):
    """Abstract configuration interface for memory system"""
    
    @property
    @abstractmethod
    def openai_api_key(self) -> str:
        pass
    
    @property
    @abstractmethod
    def model_choice(self) -> str:
        pass
    
    @property
    @abstractmethod
    def embedding_model(self) -> str:
        pass
    
    @property
    @abstractmethod
    def embedding_model_dims(self) -> int:
        pass
    
    @property
    @abstractmethod
    def memory_search_limit(self) -> Optional[int]:
        pass
    
    @property
    @abstractmethod
    def tidb_host(self) -> str:
        pass
    
    @property
    @abstractmethod  
    def tidb_port(self) -> int:
        pass
    
    @property
    @abstractmethod
    def tidb_user(self) -> str:
        pass
    
    @property
    @abstractmethod
    def tidb_password(self) -> str:
        pass
    
    @property
    @abstractmethod
    def tidb_db_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def tidb_connection_string(self) -> str:
        pass
    
    @property
    @abstractmethod
    def message_limit(self) -> int:
        pass
    
    @property
    @abstractmethod
    def summary_threshold(self) -> int:
        pass