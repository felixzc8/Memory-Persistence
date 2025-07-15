from dotenv import load_dotenv
import os
import ssl
from typing import Optional
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    model_config = {"protected_namespaces": (), "env_file": ".env"}
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_choice: str = os.getenv("MODEL_CHOICE", "gpt-4o-mini")
    
    tidb_host: str = os.getenv("TIDB_HOST", "")
    tidb_port: int = int(os.getenv("TIDB_PORT", "4000"))
    tidb_user: str = os.getenv("TIDB_USER", "")
    tidb_password: str = os.getenv("TIDB_PASSWORD", "")
    tidb_db_name: str = os.getenv("TIDB_DB_NAME", "")
    
    tidb_use_ssl: bool = True
    tidb_verify_cert: bool = True
    tidb_ssl_ca: Optional[str] = ssl.get_default_verify_paths().cafile
    embedding_model_dims: int = 1536
    mem0_collection_name: str = "mem0"
    memory_search_limit: int = 50
    
    @property
    def tidb_connection_string(self) -> str:
        """Construct TiDB connection string for SQLAlchemy"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca={self.tidb_ssl_ca}&ssl_verify_cert=true&ssl_verify_identity=true"
    
    @property
    def tidb_vector_connection_string(self) -> str:
        """Construct TiDB connection string for TiDB Vector Store"""
        return f"mysql+pymysql://{self.tidb_user}:{self.tidb_password}@{self.tidb_host}:{self.tidb_port}/{self.tidb_db_name}?ssl_ca={self.tidb_ssl_ca}&ssl_verify_cert=true&ssl_verify_identity=true"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    max_session_messages: int = int(os.getenv("MAX_SESSION_MESSAGES", "20"))
    

settings = Settings()

