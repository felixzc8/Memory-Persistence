import ssl
from typing import Optional
from pydantic_settings import BaseSettings

class MemoryConfig(BaseSettings):
    """Base configuration for memory system using Pydantic BaseSettings"""
    
    model_config = {"env_file": ".env"}
    
    # OpenAI Configuration
    openai_api_key: str = ""
    model_choice: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_model_dims: int = 1536
    
    # TiDB Configuration
    tidb_host: str = ""
    tidb_port: int = 4000
    tidb_user: str = ""
    tidb_password: str = ""
    tidb_db_name: str = ""
    tidb_use_ssl: bool = True
    tidb_verify_cert: bool = True
    tidb_ssl_ca: Optional[str] = ssl.get_default_verify_paths().cafile
    
    # Memory System Configuration
    memory_collection_name: str = "memories"
    memory_search_limit: int = 10
    message_limit: int = 20
    summary_threshold: int = 10
    
    
    @property
    def tidb_connection_string(self) -> str:
        """Construct TiDB connection string for SQLAlchemy"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca={self.tidb_ssl_ca}&ssl_verify_cert=true&ssl_verify_identity=true"