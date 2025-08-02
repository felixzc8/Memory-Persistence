import ssl
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from TiMemory package directory
load_dotenv(Path(__file__).parents[1] / ".env")

class MemoryConfig(BaseSettings):
    """Base configuration for memory system using Pydantic BaseSettings"""
    
    openai_api_key: str = ""
    model_choice: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_model_dims: int = 1536
    
    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: str = ""
    tidb_db_name: str = ""
    tidb_use_ssl: bool = True
    tidb_verify_cert: bool = True
    tidb_ssl_ca: Optional[str] = ssl.get_default_verify_paths().cafile
    
    memory_collection_name: str = "memories"
    memory_search_limit: int = 10
    max_context_message_count: int = 20
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    knowledge_graph_url: str = ""
    
    logfire_token: Optional[str] = None
    
    
    @property
    def tidb_connection_string(self) -> str:
        """Construct TiDB connection string for SQLAlchemy"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca={self.tidb_ssl_ca}&ssl_verify_cert=true&ssl_verify_identity=true"