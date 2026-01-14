"""
ASU1-Loom Backend Server
Main entry point for the FastAPI application with GraphQL endpoint

This file initializes the FastAPI application, sets up middleware,
configures GraphQL, and defines basic health check endpoints.
"""

import asyncio
import sys
import platform
from contextlib import asynccontextmanager

# Windows compatibility fix: psycopg doesn't work with ProactorEventLoop
# Switch to SelectorEventLoop on Windows for database compatibility
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from loguru import logger

from config.settings import settings
from database.connection import engine, init_db
from api.schema import Query, Mutation


# Configure logging with loguru for better debugging and monitoring
# Remove default handler and add custom ones for console and file
logger.remove()
logger.add(
    sys.stdout,  # Console output with colors
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,  # File output with rotation
    rotation="500 MB",  # Create new file when current reaches 500MB
    retention="10 days",  # Keep logs for 10 days
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager handles startup and shutdown events.
    
    Startup: Initialize database tables and log system info
    Shutdown: Close database connections gracefully
    """
    # Startup sequence
    logger.info("Starting ASU1-Loom Backend Server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")

    # Initialize database - creates tables if they don't exist
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise  # Stop server if database fails

    logger.info("ASU1-Loom Backend Server started successfully")

    yield  # Server runs and handles requests here

    # Shutdown sequence - cleanup resources
    logger.info("Shutting down ASU1-Loom Backend Server...")
    engine.dispose()  # Close all database connections
    logger.info("Cleanup completed")


# Create FastAPI application with metadata and lifespan handler
# FastAPI provides automatic API documentation at /docs
app = FastAPI(
    title="ASU1-Loom API",
    description="Hybrid Container Orchestration Platform with WASM GUI and Reverse Proxy",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware to allow frontend to call API
# This is necessary because frontend and backend run on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Allowed origins from settings
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Create GraphQL schema from Query and Mutation classes
# Strawberry provides type-safe GraphQL with Python type hints
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router and mount it at /graphql
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint - provides API information and available endpoints"""
    return {
        "message": "Welcome to ASU1-Loom API",
        "version": "1.0.0",
        "graphql": "/graphql",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy",
        "service": "loom-backend",
        "version": "1.0.0",
    }


@app.get("/info")
async def info():
    """System information endpoint - shows current configuration"""
    return {
        "service": "ASU1-Loom Backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if engine else "disconnected",
        "graphql_endpoint": "/graphql",
        "documentation": "/docs",
    }


# Run server directly with uvicorn when executed as main script
# In production, use: uvicorn main:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,  # Auto-reload on code changes in development
        log_level=settings.LOG_LEVEL.lower(),
    )
