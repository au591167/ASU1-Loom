"""
Configuration settings for ASU1-Loom Backend

Uses Pydantic Settings for type-safe configuration management.
Loads settings from environment variables (.env file) with sensible defaults.
This centralized configuration makes it easy to switch between dev/prod environments.
"""

from pydantic_settings import BaseSettings
from typing import List
import os
import platform
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation.
    
    Settings are loaded in this priority order:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values defined here (lowest priority)
    
    This allows easy configuration without code changes.
    """
    
    # ============================================================================
    # Environment Configuration
    # ============================================================================
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ============================================================================
    # API Server Configuration
    # ============================================================================
    API_HOST: str = "0.0.0.0"  # Bind to all interfaces (allows external access)
    API_PORT: int = 8000  # Port for FastAPI server
    API_RELOAD: bool = True  # Auto-reload on code changes (dev only)
    API_DEBUG: bool = True  # Enable debug mode (dev only)
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    # SQLite for simplicity - easy to demo, no separate DB server needed
    # In production, this would be PostgreSQL: "postgresql://user:pass@host/db"
    DATABASE_URL: str = "sqlite:///./loom.db"
    
    # ============================================================================
    # Docker Configuration
    # ============================================================================
    # Docker socket path - how we communicate with Docker daemon
    # Unix socket on Linux/Mac, TCP on Windows Docker Desktop
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    
    # Docker network name - all containers join this network
    # This allows containers to communicate with each other
    DOCKER_NETWORK: str = "loom_network"
    
    # ============================================================================
    # Traefik Reverse Proxy Configuration
    # ============================================================================
    # Base domain for subdomain routing
    # Example: If TRAEFIK_DOMAIN = "example.com" and subdomain = "game"
    # Then container is accessible at: game.example.com
    TRAEFIK_DOMAIN: str = "localhost"
    
    # Email for Let's Encrypt SSL certificates (production only)
    TRAEFIK_EMAIL: str = "admin@example.com"
    
    # ============================================================================
    # Security Configuration
    # ============================================================================
    SECRET_KEY: str = "your-secret-key-change-in-production"  # For JWT signing
    JWT_ALGORITHM: str = "HS256"  # JWT signing algorithm
    JWT_EXPIRATION_HOURS: int = 24  # How long tokens are valid
    
    # ============================================================================
    # CORS (Cross-Origin Resource Sharing) Configuration
    # ============================================================================
    # Allowed origins for frontend to call backend API
    # In production, this should be restricted to your actual frontend domain
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend dev server
        "http://localhost:8000",  # Backend (for GraphQL playground)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # ============================================================================
    # Logging Configuration
    # ============================================================================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "logs/loom.log"  # Where to write log files
    
    # ============================================================================
    # Container Default Settings
    # ============================================================================
    DEFAULT_NETWORK: str = "loom_network"  # Default network for new containers
    DEFAULT_RESTART_POLICY: str = "unless-stopped"  # Auto-restart containers
    
    # Pydantic configuration
    model_config = {
        "env_file": "../.env",  # Look for .env file in parent directory
        "env_file_encoding": "utf-8",
        "case_sensitive": True,  # Environment variables are case-sensitive
        "extra": "ignore"  # Ignore extra fields from .env that aren't defined here
    }


# ============================================================================
# Create Global Settings Instance
# ============================================================================
# This singleton instance is imported throughout the application
settings = Settings()

# ============================================================================
# Platform-Specific Docker Configuration
# ============================================================================
# Docker Desktop uses different connection methods on different OS
if platform.system() == "Windows":
    # Windows Docker Desktop uses TCP connection
    settings.DOCKER_HOST = "tcp://localhost:2375"
elif platform.system() == "Darwin":  # macOS
    # macOS Docker Desktop uses Unix socket
    settings.DOCKER_HOST = "unix:///var/run/docker.sock"
else:
    # Linux uses Unix socket (standard Docker installation)
    settings.DOCKER_HOST = "unix:///var/run/docker.sock"

# ============================================================================
# Ensure Required Directories Exist
# ============================================================================
# Create logs directory if it doesn't exist
# This prevents errors when trying to write log files
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)
