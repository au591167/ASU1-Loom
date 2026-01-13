"""
Database connection and session management
Using synchronous psycopg for Windows compatibility
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from loguru import logger
import asyncio
from functools import wraps

from config.settings import settings


# Handle different database URLs
database_url = settings.DATABASE_URL
# For SQLite, ensure proper URL format
if database_url.startswith("sqlite"):
    pass  # SQLite URLs are fine as-is
# For PostgreSQL, ensure we're using psycopg (not psycopg2)
elif "postgresql://" in database_url and "postgresql+psycopg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

# Create synchronous engine (works on Windows!)
engine = create_engine(
    database_url,
    echo=settings.API_DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency for getting database session (synchronous)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


async def init_db():
    """
    Initialize database - create all tables
    Runs synchronous code in executor for async compatibility
    """
    def _create_tables():
        try:
            # Import all models to ensure they're registered
            from models import container, user
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # Run in executor to make it async-compatible
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _create_tables)
