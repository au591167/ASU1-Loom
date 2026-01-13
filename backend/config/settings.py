"""
Configuration settings for ASU1-Loom Backend
Loads environment variables and provides application configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os
import platform
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./loom.db"  # Use SQLite for local development/demo
    
    # Docker Configuration
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    DOCKER_NETWORK: str = "loom_network"
    
    # Traefik Configuration
    TRAEFIK_DOMAIN: str = "localhost"
    TRAEFIK_EMAIL: str = "admin@example.com"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/loom.log"
    
    # Container Defaults
    DEFAULT_NETWORK: str = "loom_network"
    DEFAULT_RESTART_POLICY: str = "unless-stopped"
    
    model_config = {
        "env_file": "../.env",  # Look for .env in parent directory
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from .env
    }


# Create settings instance
settings = Settings()

# Platform-specific Docker host configuration
if platform.system() == "Windows":
    # Windows Docker Desktop typically uses TCP
    settings.DOCKER_HOST = "tcp://localhost:2375"
elif platform.system() == "Darwin":  # macOS
    # macOS Docker Desktop might use Unix socket or TCP
    settings.DOCKER_HOST = "unix:///var/run/docker.sock"
else:
    # Linux and others
    settings.DOCKER_HOST = "unix:///var/run/docker.sock"

# Ensure logs directory exists
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)
