"""
Configuration module for TravelAI Booking System
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    anthropic_api_key: str
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Vector DB
    chroma_path: str = "./data/chroma"
    
    # Redis (optional)
    redis_url: Optional[str] = None
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Security
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Agent Config
    agent_timeout_seconds: int = 60
    max_tool_calls_per_request: int = 10
    conversation_history_limit: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Load settings
settings = Settings()