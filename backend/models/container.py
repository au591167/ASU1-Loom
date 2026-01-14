"""
Container model for storing container metadata

SQLAlchemy ORM model that represents the 'containers' table in the database.
Stores persistent metadata about Docker containers, allowing us to track
containers even if Docker restarts or the application is redeployed.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
from database.connection import Base


class Container(Base):
    """
    Container model representing a Docker container managed by Loom.
    
    This model stores all container configuration and metadata in PostgreSQL/SQLite.
    Why store in database when Docker already tracks containers?
    - Persist data across Docker restarts
    - Store additional metadata not in Docker (description, user_id)
    - Enable complex queries (find all containers by user, status, etc.)
    - Track historical data (when started/stopped)
    """
    __tablename__ = "containers"
    
    # ============================================================================
    # Primary Key
    # ============================================================================
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ============================================================================
    # Container Identification
    # ============================================================================
    # Docker's internal container ID (12-character hash like "a1b2c3d4e5f6")
    # Nullable because container might not be created in Docker yet
    container_id = Column(String(64), unique=True, index=True, nullable=True)
    
    # User-friendly name (must be unique, used in Traefik routing)
    name = Column(String(255), unique=True, index=True, nullable=False)
    
    # ============================================================================
    # Container Configuration
    # ============================================================================
    # Docker image name (e.g., "nginx", "itzg/minecraft-server")
    image = Column(String(255), nullable=False)
    
    # Image version tag (e.g., "latest", "1.20.1", "alpine")
    tag = Column(String(50), default="latest")
    
    # ============================================================================
    # Network Configuration
    # ============================================================================
    # Subdomain for Traefik routing (e.g., "game" -> game.domain.com)
    # Must be unique to avoid routing conflicts
    subdomain = Column(String(255), unique=True, index=True, nullable=False)
    
    # Port the application listens on inside the container
    internal_port = Column(Integer, nullable=False)
    
    # Optional direct port mapping (bypasses Traefik)
    # Example: 25565 for Minecraft to allow direct connections
    external_port = Column(Integer, nullable=True)
    
    # ============================================================================
    # Container Settings
    # ============================================================================
    # Environment variables as JSON object
    # Example: {"EULA": "TRUE", "DIFFICULTY": "hard"}
    environment_vars = Column(JSON, default={})
    
    # Volume mappings as JSON array
    # Example: ["/host/path:/container/path", "/data:/minecraft/data"]
    volumes = Column(JSON, default=[])
    
    # Custom command to override container's default CMD
    # Example: "java -Xmx2G -jar server.jar"
    command = Column(Text, nullable=True)
    
    # ============================================================================
    # Resource Limits
    # ============================================================================
    # Memory limit in Docker format (e.g., "512m", "2g")
    # Prevents containers from consuming all system RAM
    memory_limit = Column(String(20), nullable=True)
    
    # CPU limit as fraction of cores (e.g., "0.5" = half a core, "2.0" = 2 cores)
    cpu_limit = Column(String(20), nullable=True)
    
    # ============================================================================
    # Status and Lifecycle
    # ============================================================================
    # Current container status: created, running, stopped, error
    status = Column(String(50), default="created")
    
    # When to restart container: unless-stopped, always, no, on-failure
    restart_policy = Column(String(50), default="unless-stopped")
    
    # ============================================================================
    # Metadata
    # ============================================================================
    # User-provided description for documentation
    description = Column(Text, nullable=True)
    
    # Custom Docker labels as JSON (can be used for filtering, grouping)
    labels = Column(JSON, default={})
    
    # ============================================================================
    # Timestamps
    # ============================================================================
    # When record was created in database (auto-set by database)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # When record was last updated (auto-updated by database)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # When container was last started (set by application)
    started_at = Column(DateTime(timezone=True), nullable=True)
    
    # When container was last stopped (set by application)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    
    # ============================================================================
    # Multi-User Support (Future Feature)
    # ============================================================================
    # ID of user who owns this container
    # Allows filtering containers by user, implementing permissions, etc.
    user_id = Column(Integer, nullable=True, index=True)
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Container(name={self.name}, image={self.image}, status={self.status})>"
    
    def to_dict(self):
        """
        Convert model to dictionary for JSON serialization.
        
        Useful for REST APIs or logging.
        GraphQL uses the ContainerType instead.
        """
        return {
            "id": self.id,
            "container_id": self.container_id,
            "name": self.name,
            "image": self.image,
            "tag": self.tag,
            "subdomain": self.subdomain,
            "internal_port": self.internal_port,
            "external_port": self.external_port,
            "environment_vars": self.environment_vars,
            "volumes": self.volumes,
            "command": self.command,
            "memory_limit": self.memory_limit,
            "cpu_limit": self.cpu_limit,
            "status": self.status,
            "restart_policy": self.restart_policy,
            "description": self.description,
            "labels": self.labels,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "user_id": self.user_id,
        }
