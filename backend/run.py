"""
Startup script for ASU1-Loom Backend
Handles Windows event loop compatibility
"""

import asyncio
import platform
import sys

# Fix for Windows ProactorEventLoop incompatibility with psycopg
if platform.system() == 'Windows':
    # Set the event loop policy before anything else
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print("✅ Windows SelectorEventLoop policy set for psycopg compatibility")

if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    
    print(f"🚀 Starting ASU1-Loom Backend on {settings.API_HOST}:{settings.API_PORT}")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,  # Disable reload to avoid WatchFiles issues
        log_level=settings.LOG_LEVEL.lower(),
        loop="asyncio",
    )
