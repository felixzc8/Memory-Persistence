from dotenv import load_dotenv
import os
from typing import Optional
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    model_config = {"protected_namespaces": (), "env_file": ".env"}
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_choice: str = os.getenv("MODEL_CHOICE", "gpt-4o-mini")
    
    # TiDB Configuration
    tidb_host: str = os.getenv("TIDB_HOST", "")
    tidb_port: int = int(os.getenv("TIDB_PORT", "4000"))
    tidb_user: str = os.getenv("TIDB_USER", "")
    tidb_password: str = os.getenv("TIDB_PASSWORD", "")
    tidb_db_name: str = os.getenv("TIDB_DB_NAME", "")
    
    # TiDB Native Provider Configuration
    tidb_use_ssl: bool = True
    tidb_verify_cert: bool = True
    tidb_ssl_ca: Optional[str] = "/etc/ssl/cert.pem"
    embedding_model_dims: int = 1536  # OpenAI text-embedding-3-small dimensions
    
    # Mem0 Configuration
    mem0_collection_name: str = "mem0"
    memory_search_limit: int = 50
    
    # Legacy TiDB Vector Configuration (for backward compatibility)
    tidb_vector_table_name: str = "memory_vectors"
    tidb_vector_distance_strategy: str = "cosine"  # "cosine" or "l2"
    
    @property
    def tidb_connection_string(self) -> str:
        """Construct TiDB connection string for SQLAlchemy"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
    
    @property
    def tidb_vector_connection_string(self) -> str:
        """Construct TiDB connection string for TiDB Vector Store"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Session Configuration
    session_ttl_hours: int = int(os.getenv("SESSION_TTL_HOURS", "24"))
    max_session_messages: int = int(os.getenv("MAX_SESSION_MESSAGES", "20"))
    session_cleanup_interval_hours: int = int(os.getenv("SESSION_CLEANUP_INTERVAL_HOURS", "6"))
    

settings = Settings()

