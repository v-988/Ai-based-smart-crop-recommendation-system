"""
Configuration settings for the Plant Disease Detection API.
Uses Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All sensitive data should be stored in .env file.
    """
    
    # API Information
    APP_NAME: str = "Plant Disease Detection & Farmer Chatbot API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered plant disease detection and agricultural chatbot"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,https://your-frontend-domain.vercel.app"
    
    # HuggingFace API Configuration
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL_URL: str = "https://router.huggingface.co/hf-inference/models/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "arcee-ai/trinity-mini:free"
    OPENROUTER_FALLBACK_MODELS: str = "nvidia/nemotron-3-super-120b-a12b:free,stepfun/step-3.5-flash:free,arcee-ai/trinity-large-preview:free,liquid/lfm-2.5-1.2b-thinking:free,liquid/lfm-2.5-1.2b-instruct:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Groq API Configuration (fallback provider)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FALLBACK_MODELS: str = "llama-3.3-70b-versatile,llama-3.1-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    
    # Chat Configuration
    MAX_CHAT_HISTORY: int = 10
    MAX_TOKENS: int = 500
    TEMPERATURE: float = 0.3
    MAX_CONTINUATION_LOOPS: int = 1
    
    # File Upload Configuration
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp,image/gif"
    
    # Voice Configuration
    TEMP_AUDIO_DIR: str = "temp_audio"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Uses LRU cache to avoid reading .env file on every request.
    """
    return Settings()


# Create temp directory if not exists
settings = get_settings()
os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)
