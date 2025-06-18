from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model_choice: str = os.getenv("MODEL_CHOICE", "gpt-4o-mini")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Mem0 Configuration
    mem0_collection_name: str = "memories"
    memory_search_limit: int = 3
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

# Backward compatibility for existing imports
OPENAI_API_KEY = settings.openai_api_key
MODEL_CHOICE = settings.model_choice
DATABASE_URL = settings.database_url
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key

