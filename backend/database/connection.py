"""
Database connection and session management

Uses async SQLAlchemy for non-blocking database operations.
Supports both SQLite (development) and PostgreSQL (production).
This allows the API to handle multiple requests concurrently without blocking.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger
import asyncio

from config.settings import settings


# ============================================================================
# Database URL Configuration
# ============================================================================
# Get database URL from settings
database_url = settings.DATABASE_URL

# Convert standard database URLs to async-compatible format
# SQLAlchemy async requires specific drivers:
# - asyncpg for PostgreSQL (fast, pure Python)
# - aiosqlite for SQLite (async wrapper)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
elif database_url.startswith("sqlite://"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

# ============================================================================
# Create Async Database Engine
# ============================================================================
# The engine manages the connection pool to the database
engine = create_async_engine(
    database_url,
    echo=settings.API_DEBUG,  # Log all SQL queries when debugging
    future=True,  # Use SQLAlchemy 2.0 style
    pool_pre_ping=True,  # Verify connections before using (prevents stale connections)
)

# ============================================================================
# Create Async Session Factory
# ============================================================================
# Sessions are used for database transactions
# Each request gets its own session via dependency injection
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Use async session class
    autocommit=False,  # Manual transaction control
    autoflush=False,  # Manual flush control
)

# ============================================================================
# Create Declarative Base
# ============================================================================
# All database models inherit from this base class
# It tracks all models and their metadata (tables, columns, relationships)
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency injection function for database sessions.
    
    Used in FastAPI/GraphQL resolvers to get a database session.
    Automatically handles:
    - Session creation
    - Transaction commit on success
    - Transaction rollback on error
    - Session cleanup
    
    Usage in GraphQL resolver:
        async for session in get_db():
            # Use session here
            result = await session.execute(query)
    """
    async with async_session() as session:
        try:
            yield session  # Provide session to caller
            await session.commit()  # Commit transaction if no errors
        except Exception as e:
            await session.rollback()  # Rollback on any error
            logger.error(f"Database session error: {e}")
            raise  # Re-raise to inform caller


async def init_db():
    """
    Initialize database by creating all tables.
    
    Called during application startup (in main.py lifespan).
    Creates tables for all models that inherit from Base.
    Safe to call multiple times - won't recreate existing tables.
    """
    try:
        # Import all models to register them with Base
        # This ensures SQLAlchemy knows about all tables
        from models import container, user

        # Create all tables defined in models
        # run_sync() is needed because create_all() is synchronous
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
