"""
Logging configuration for the application.
Uses Loguru for structured logging.
"""

import sys
from loguru import logger
from config.settings import settings


def setup_logging():
    """
    Configure application logging with Loguru.
    Sets up console and file logging with proper formatting.
    """
    # Remove default handler
    logger.remove()
    
    # Console logging format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # File logging format
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file handler for production
    if not settings.DEBUG:
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            format=file_format,
            level="INFO",
            rotation="1 day",
            retention="7 days",
            compression="gz",
            backtrace=True,
            diagnose=False
        )
        
        # Error-only log file
        logger.add(
            "logs/errors_{time:YYYY-MM-DD}.log",
            format=file_format,
            level="ERROR",
            rotation="1 day",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True
        )
    
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")
    
    return logger


# Export configured logger
app_logger = logger
