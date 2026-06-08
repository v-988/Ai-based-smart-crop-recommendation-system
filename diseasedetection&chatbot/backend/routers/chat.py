"""
Chat Router
Handles AI chatbot endpoints with streaming support.
"""

import json
from fastapi import APIRouter, HTTPException, status, Query, Header
from fastapi.responses import StreamingResponse
from loguru import logger
from typing import Optional

from models.schemas import ChatRequest, ChatResponse, LanguageEnum, ErrorResponse
from services.llm_service import llm_service
from utils.helpers import generate_session_id

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        200: {"description": "Chat response generated"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Send chat message",
    description="""
    Send a message to the agricultural AI chatbot.
    
    Features:
    - Context-aware responses based on detected disease
    - Chat history memory within session
    - Tamil and English language support
    - Auto language detection
    
    Headers:
    - X-Session-ID: Optional session ID for conversation continuity
    """
)
async def chat(
    request: ChatRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Process chat message and return AI response.
    
    Args:
        request: Chat request with message and context
        x_session_id: Optional session ID for continuity
        
    Returns:
        AI response with language info
    """
    try:
        # Generate session ID if not provided
        session_id = x_session_id or generate_session_id()
        
        logger.info(f"Chat request - Session: {session_id[:8]}...")
        
        # Get AI response
        response = await llm_service.chat(
            message=request.message,
            session_id=session_id,
            disease_context=request.disease_context,
            language=request.language
        )
        
        # Detect response language
        detected_language = llm_service._detect_language(response)
        
        return ChatResponse(
            response=response,
            language=detected_language
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/stream",
    summary="Stream chat response",
    description="""
    Stream chat response for real-time display.
    Returns Server-Sent Events (SSE) stream.
    
    Event format:
    - data: {"content": "response chunk", "done": false}
    - data: {"content": "", "done": true}
    """
)
async def chat_stream(
    request: ChatRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """
    Stream AI response in real-time.
    
    Args:
        request: Chat request
        x_session_id: Session ID
        
    Returns:
        SSE stream of response chunks
    """
    session_id = x_session_id or generate_session_id()
    
    async def generate():
        try:
            async for chunk in llm_service.chat_stream(
                message=request.message,
                session_id=session_id,
                disease_context=request.disease_context,
                language=request.language
            ):
                data = json.dumps({"content": chunk, "done": False})
                yield f"data: {data}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-ID": session_id
        }
    )


@router.delete(
    "/history",
    summary="Clear chat history",
    description="Clear chat history for a session"
)
async def clear_history(
    x_session_id: str = Header(..., alias="X-Session-ID")
):
    """
    Clear chat history for a session.
    
    Args:
        x_session_id: Session ID to clear
        
    Returns:
        Success confirmation
    """
    try:
        llm_service.clear_session(x_session_id)
        return {"message": "Chat history cleared", "session_id": x_session_id}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/languages",
    summary="Get supported languages",
    description="Get list of supported chat languages"
)
async def get_languages():
    """
    Get list of supported languages.
    
    Returns:
        List of language options
    """
    return {
        "languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "ta", "name": "Tamil", "native": "தமிழ்"}
        ]
    }
