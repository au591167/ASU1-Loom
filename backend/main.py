"""
ASU1-Loom Backend Server
Main entry point for the FastAPI application with GraphQL endpoint
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from loguru import logger
import sys

from config.settings import settings
from database.connection import engine, init_db
from api.schema import Query, Mutation


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting ASU1-Loom Backend Server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("✅ ASU1-Loom Backend Server started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ASU1-Loom Backend Server...")
    await engine.dispose()
    logger.info("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title="ASU1-Loom API",
    description="Hybrid Container Orchestration Platform with WASM GUI and Reverse Proxy",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ASU1-Loom API",
        "version": "1.0.0",
        "graphql": "/graphql",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "loom-backend",
        "version": "1.0.0",
    }


@app.get("/info")
async def info():
    """System information endpoint"""
    return {
        "service": "ASU1-Loom Backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if engine else "disconnected",
        "graphql_endpoint": "/graphql",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
