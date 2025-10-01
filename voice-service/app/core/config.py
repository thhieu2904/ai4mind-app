"""
Voice Analysis Service - Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str
    
    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8000"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # File Storage
    FILE_STORAGE_PATH: str = "./storage/audio"
    MAX_FILE_SIZE_MB: int = 10
    
    # Whisper
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    
    # Processing
    ENABLE_EMOTION_DETECTION: bool = True
    ENABLE_TEXT_ANALYSIS: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Voice Analysis Service"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
