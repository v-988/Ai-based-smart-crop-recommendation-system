"""
Models package initialization.
Exports all schema models for easy import.
"""

from .schemas import (
    LanguageEnum,
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
    ChatRequest,
    ChatResponse,
    VoiceInputRequest,
    VoiceOutputRequest,
    ChatMessage,
    ChatHistory,
    HealthCheckResponse,
    ErrorResponse
)

__all__ = [
    "LanguageEnum",
    "DiseaseDetectionRequest",
    "DiseaseDetectionResponse",
    "ChatRequest",
    "ChatResponse",
    "VoiceInputRequest",
    "VoiceOutputRequest",
    "ChatMessage",
    "ChatHistory",
    "HealthCheckResponse",
    "ErrorResponse"
]
