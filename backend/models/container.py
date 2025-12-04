"""
Container model for storing container metadata
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
from database.connection import Base


class Container(Base):
    """
    Container model representing a Docker container managed by Loom
    """
    __tablename__ = "containers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Container identification
    container_id = Column(String(64), unique=True, index=True, nullable=True)  # Docker container ID
    name = Column(String(255), unique=True, index=True, nullable=False)
    
    # Container configuration
    image = Column(String(255), nullable=False)
    tag = Column(String(50), default="latest")
    
    # Network configuration
    subdomain = Column(String(255), unique=True, index=True, nullable=False)
    internal_port = Column(Integer, nullable=False)
    external_port = Column(Integer, nullable=True)
    
    # Container settings
    environment_vars = Column(JSON, default={})  # Environment variables as JSON
    volumes = Column(JSON, default=[])  # Volume mappings as JSON array
    command = Column(Text, nullable=True)  # Custom command to run
    
    # Resource limits
    memory_limit = Column(String(20), nullable=True)  # e.g., "512m", "1g"
    cpu_limit = Column(String(20), nullable=True)  # e.g., "0.5", "1.0"
    
    # Status
    status = Column(String(50), default="created")  # created, running, stopped, error
    restart_policy = Column(String(50), default="unless-stopped")
    
    # Metadata
    description = Column(Text, nullable=True)
    labels = Column(JSON, default={})  # Custom labels as JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    
    # User association (for future multi-user support)
    user_id = Column(Integer, nullable=True, index=True)
    
    def __repr__(self):
        return f"<Container(name={self.name}, image={self.image}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
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
