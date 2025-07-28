from dotenv import load_dotenv
import os
from typing import Optional
from TiMemory.config.base import MemoryConfig

load_dotenv()

class Settings(MemoryConfig):
    model_config = {"protected_namespaces": (), "env_file": ".env"}
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_choice: str = os.getenv("MODEL_CHOICE", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    tidb_host: str = os.getenv("TIDB_HOST", "")
    tidb_port: int = int(os.getenv("TIDB_PORT", 4000))
    tidb_user: str = os.getenv("TIDB_USER", "")
    tidb_password: str = os.getenv("TIDB_PASSWORD", "")
    tidb_db_name: str = os.getenv("TIDB_DB_NAME", "")
    
    
    # Backend-specific settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    logfire_token: Optional[str] = os.getenv("LOGFIRE_TOKEN")
    

settings = Settings()

