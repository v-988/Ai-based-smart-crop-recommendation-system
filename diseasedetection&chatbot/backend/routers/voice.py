"""
Voice Router
Handles speech-to-text and text-to-speech endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import StreamingResponse, Response
from loguru import logger
from typing import Optional
import io

from models.schemas import VoiceOutputRequest, LanguageEnum, ErrorResponse
from services.speech_service import speech_service

router = APIRouter(prefix="/voice", tags=["Voice Processing"])


@router.post(
    "/transcribe",
    summary="Convert speech to text",
    description="""
    Upload audio file and convert to text.
    
    Supported formats: WAV, MP3, WebM, OGG
    Supports Tamil and English languages.
    Auto-detects language if not specified.
    """,
    responses={
        200: {"description": "Transcription successful"},
        400: {"model": ErrorResponse, "description": "Invalid audio"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[LanguageEnum] = Query(
        None,
        description="Language hint (optional)"
    )
):
    """
    Convert uploaded audio to text.
    
    Args:
        audio: Audio file (WAV, MP3, WebM, OGG)
        language: Optional language hint
        
    Returns:
        Transcribed text and detected language
    """
    try:
        # Read audio bytes
        audio_bytes = await audio.read()
        
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )
        
        # Limit audio size (50MB max)
        if len(audio_bytes) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file too large. Maximum 50MB."
            )
        
        logger.info(
            f"Transcribing audio: {audio.filename} "
            f"({len(audio_bytes)} bytes)"
        )
        
        # Transcribe
        text, detected_language = await speech_service.speech_to_text(
            audio_bytes,
            language,
            filename=audio.filename
        )
        
        return {
            "text": text,
            "language": detected_language.value,
            "language_code": "ta" if detected_language == LanguageEnum.TAMIL else "en"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/synthesize",
    summary="Convert text to speech",
    description="""
    Convert text to speech audio (MP3).
    
    Supports Tamil and English languages.
    Returns MP3 audio bytes.
    """,
    responses={
        200: {
            "description": "Audio generated successfully",
            "content": {"audio/mpeg": {}}
        },
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def synthesize_speech(request: VoiceOutputRequest):
    """
    Convert text to speech audio.
    
    Args:
        request: Text and language settings
        
    Returns:
        MP3 audio stream
    """
    try:
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        logger.info(
            f"Synthesizing speech: {len(request.text)} chars, "
            f"{request.language.value}"
        )
        
        # Generate audio
        audio_bytes = await speech_service.text_to_speech(
            request.text,
            request.language
        )
        
        # Return as streaming response
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/synthesize/stream",
    summary="Stream text to speech",
    description="Convert text to speech with streaming response"
)
async def synthesize_speech_stream(request: VoiceOutputRequest):
    """
    Stream text-to-speech audio.
    
    Args:
        request: Text and language settings
        
    Returns:
        Streaming MP3 audio
    """
    try:
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Get audio stream
        audio_stream = await speech_service.text_to_speech_stream(
            request.text,
            request.language
        )
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/languages",
    summary="Get supported voice languages",
    description="Get list of languages supported for voice input/output"
)
async def get_voice_languages():
    """
    Get supported voice languages.
    
    Returns:
        List of supported languages for TTS and STT
    """
    return {
        "tts_languages": [
            {"code": "en", "name": "English"},
            {"code": "ta", "name": "Tamil"}
        ],
        "stt_languages": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "ta-IN", "name": "Tamil (India)"}
        ]
    }
