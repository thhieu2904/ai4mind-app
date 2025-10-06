"""
Voice Analysis Service - Configuration
Hybrid architecture: Deepgram API + Custom Emotion ML
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings for Hybrid Voice Service.
    
    Architecture Change (2025-10-06):
    ✅ BEFORE: Whisper (local) → 512MB+ RAM → Build failed
    ✅ AFTER: Deepgram API (external) → <512MB RAM → Deploy OK!
    
    Key Changes:
    - Added DEEPGRAM_API_KEY (required)
    - Deprecated WHISPER_MODEL (optional, kept for fallback)
    - Kept emotion detection settings (our unique value!)
    """
    
    # Database (REQUIRED)
    DATABASE_URL: str
    
    # AI Service (REQUIRED for production)
    AI_SERVICE_URL: str  # No default - must be set via environment
    
    # Deepgram API (REQUIRED for transcription)
    DEEPGRAM_API_KEY: str  # Get free key at https://console.deepgram.com
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # File Storage (use /tmp for production - always writable on Linux)
    FILE_STORAGE_PATH: str = "./storage/audio"  # Local dev default
    MAX_FILE_SIZE_MB: int = 10
    
    # Transcription Service Selection
    TRANSCRIPTION_SERVICE: str = "deepgram"  # "deepgram" or "whisper" (fallback)
    
    # Whisper (DEPRECATED - kept for local development only)
    WHISPER_MODEL: Optional[str] = "base"  # tiny, base, small, medium, large
    # Note: Whisper requires 512MB+ RAM, not deployable on free tier!
    
    # Processing (KEPT - our custom ML!)
    ENABLE_EMOTION_DETECTION: bool = True
    ENABLE_TEXT_ANALYSIS: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI4Mind Voice Analysis (Hybrid)"
    VERSION: str = "2.0.0"  # v2.0: Hybrid architecture
    DESCRIPTION: str = "Speech-to-text via Deepgram API + Custom emotion detection ML"
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def use_deepgram(self) -> bool:
        """Check if should use Deepgram API"""
        return (
            self.TRANSCRIPTION_SERVICE.lower() == "deepgram" 
            and bool(self.DEEPGRAM_API_KEY)
        )
    
    def validate_config(self):
        """
        Validate critical configuration.
        Call this at startup to fail fast if misconfigured.
        """
        errors = []
        
        # Check required fields
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        if not self.AI_SERVICE_URL:
            errors.append("AI_SERVICE_URL is required")
        
        # Check transcription service
        if self.use_deepgram:
            if not self.DEEPGRAM_API_KEY:
                errors.append(
                    "DEEPGRAM_API_KEY is required when TRANSCRIPTION_SERVICE=deepgram. "
                    "Get free key at https://console.deepgram.com"
                )
        elif self.TRANSCRIPTION_SERVICE.lower() == "whisper":
            errors.append(
                "WARNING: Whisper requires 512MB+ RAM and won't deploy on free tier! "
                "Consider using TRANSCRIPTION_SERVICE=deepgram instead."
            )
        
        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )


# Create settings instance
settings = Settings()

