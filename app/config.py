import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "Mulu AI Agent Backend"
    APP_VERSION: str = "6.0.0"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # AI Configuration
    AI_MODEL: str = "gpt-4"
    OPENAI_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # World Configuration
    MAX_WORLDS_PER_NODE: int = 100
    DEFAULT_TICK_RATE: str = "fast"
    WORLD_SEED_PREFIX: str = "mulu"
    
    # Resource Budget
    MAX_TOKENS_PER_WORLD: int = 100000
    MAX_SPAWNS_PER_WORLD: int = 50
    MAX_CONCURRENT_REQUESTS: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

# Global settings instance
settings = Settings()
