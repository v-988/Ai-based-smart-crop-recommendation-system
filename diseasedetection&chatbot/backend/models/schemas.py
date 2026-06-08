"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported languages for the chatbot."""
    ENGLISH = "English"
    TAMIL = "Tamil"


class DiseaseDetectionRequest(BaseModel):
    """Request model for disease detection (handled via form-data)."""
    pass  # Image is handled separately via UploadFile


class DiseaseDetectionResponse(BaseModel):
    """Response model for disease detection results."""
    disease: str = Field(..., description="Detected disease name")
    confidence: float = Field(..., description="Confidence score (0-1)")
    recommendations: Optional[List[str]] = Field(
        None, 
        description="Treatment recommendations"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "disease": "Tomato___Late_blight",
                "confidence": 0.95,
                "recommendations": [
                    "Remove infected leaves",
                    "Apply copper-based fungicide"
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    disease_context: Optional[str] = Field(None, description="Detected disease for context")
    language: Optional[LanguageEnum] = Field(None, description="Preferred response language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "How do I treat this disease?",
                "disease_context": "Tomato___Late_blight",
                "language": "English"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str = Field(..., description="AI response")
    language: LanguageEnum = Field(..., description="Response language")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "To treat Late Blight, follow these steps...",
                "language": "English",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class VoiceInputRequest(BaseModel):
    """Request model for voice input (handled via form-data)."""
    pass  # Audio is handled separately via UploadFile


class VoiceOutputRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert")
    language: LanguageEnum = Field(LanguageEnum.ENGLISH, description="Voice language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Your plant has Late Blight disease.",
                "language": "English"
            }
        }


class ChatMessage(BaseModel):
    """Model for a single chat message in history."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Model for chat history storage."""
    session_id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
