#!/usr/bin/env python3
"""
Entry point for Mulu AI Agent Backend.
Run: python main.py
"""

import uvicorn
from app.config import settings
from app.utils.logger import logger, setup_logging

if __name__ == "__main__":
    # Setup logging
    setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1 if settings.DEBUG else settings.WORKERS,
    )
