"""
Plant Disease Detection & Farmer Chatbot API
Main FastAPI application entry point.

This application provides:
- Plant disease detection using AI image classification
- Agricultural chatbot with Tamil and English support
- Voice input/output capabilities
- Real-time streaming responses

Author: Plant AI Team
Version: 1.0.0
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import uvicorn

from config.settings import settings, get_settings
from routers import detect_router, chat_router, voice_router
from utils.logger import setup_logging
from models.schemas import HealthCheckResponse, ErrorResponse


# Setup logging on startup
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 50)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 50)
    
    # Create necessary directories
    os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Validate API keys
    if not settings.HUGGINGFACE_API_KEY:
        logger.warning("HUGGINGFACE_API_KEY not configured!")
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not configured!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Cleanup temp files
    from utils.helpers import cleanup_temp_files
    cleanup_temp_files(settings.TEMP_AUDIO_DIR)
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS
cors_origins = [
    origin.strip() 
    for origin in settings.CORS_ORIGINS.split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID"]
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    """Handle validation errors with detailed messages."""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    logger.warning(f"Validation error: {error_messages}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": error_messages
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again."
        }
    )


# Include routers
app.include_router(detect_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")


# Root endpoints
@app.get(
    "/",
    summary="Root endpoint",
    description="Welcome message and API info"
)
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check API health status"
)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.get(
    "/api/v1/status",
    summary="API status",
    description="Detailed API status and configuration"
)
async def api_status():
    """Get detailed API status."""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "features": {
            "disease_detection": bool(settings.HUGGINGFACE_API_KEY),
            "chatbot": bool(settings.OPENROUTER_API_KEY),
            "voice_input": True,
            "voice_output": True,
            "streaming": True
        },
        "languages": ["English", "Tamil"],
        "endpoints": {
            "detect": "/api/v1/detect",
            "chat": "/api/v1/chat",
            "chat_stream": "/api/v1/chat/stream",
            "voice_transcribe": "/api/v1/voice/transcribe",
            "voice_synthesize": "/api/v1/voice/synthesize"
        }
    }


# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
