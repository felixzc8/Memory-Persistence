from dotenv import load_dotenv
from typing import Optional
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Backend API configuration - only API-specific settings"""
    model_config = {"env_file": ".env"}
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    logfire_token: Optional[str] = None

settings = Settings()

