"""
Configuration Management
Load settings from environment variables
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Get project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application Settings"""
    
    # App Info
    APP_NAME: str = "AI4Mind API Gateway"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    
    # Database - Read from SUPABASE_DATABASE_URL env variable
    DATABASE_URL: str = "postgresql://localhost/ai4mind"
    
    # Supabase (for Storage and RLS)
    SUPABASE_PROJECT_URL: str = ""
    SUPABASE_ANON_KEY: str = ""  # For client-side access
    SUPABASE_SERVICE_ROLE_KEY: str = ""  # For server-side admin access
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Microservices
    VOICE_SERVICE_URL: str = "http://localhost:8001"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]
    
    # File Upload
    UPLOAD_DIR: str = "../shared/audio-files"
    MAX_FILE_SIZE: int = 52428800  # 50MB
    
    class Config:
        env_file = str(ENV_FILE)  # Use absolute path to .env
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create settings instance
settings = Settings()
