"""
Routers package initialization.
Exports all API routers.
"""

from .detect import router as detect_router
from .chat import router as chat_router
from .voice import router as voice_router

__all__ = [
    "detect_router",
    "chat_router", 
    "voice_router"
]
