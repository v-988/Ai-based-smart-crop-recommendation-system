"""
Disease Detection Router
Handles plant disease detection endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger

from models.schemas import DiseaseDetectionResponse, ErrorResponse
from services.disease_service import disease_service
from config.settings import settings
from utils.helpers import validate_image_type

router = APIRouter(prefix="/detect", tags=["Disease Detection"])


@router.post(
    "",
    response_model=DiseaseDetectionResponse,
    responses={
        200: {"description": "Disease detected successfully"},
        400: {"model": ErrorResponse, "description": "Invalid image"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Detect plant disease from image",
    description="""
    Upload a plant leaf image to detect diseases.
    
    Supported formats: JPEG, PNG, WebP, GIF
    Maximum size: 10MB
    
    Returns:
    - Disease name
    - Confidence score (0-1)
    - Treatment recommendations
    """
)
async def detect_disease(
    image: UploadFile = File(..., description="Plant leaf image file")
):
    """
    Detect plant disease from uploaded image.
    
    Args:
        image: Uploaded image file
        
    Returns:
        Disease detection results with recommendations
    """
    try:
        # Validate file type
        if not validate_image_type(
            image.content_type,
            settings.ALLOWED_IMAGE_TYPES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # Read image bytes
        image_bytes = await image.read()
        
        # Validate file size
        if len(image_bytes) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image too large. Maximum size: {settings.MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        logger.info(f"Processing image: {image.filename} ({len(image_bytes)} bytes)")
        
        # Detect disease
        disease, confidence, recommendations = await disease_service.detect_disease(
            image_bytes
        )
        
        return DiseaseDetectionResponse(
            disease=disease,
            confidence=confidence,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/all",
    response_model=list,
    summary="Get all disease predictions",
    description="Get top-k disease predictions with confidence scores"
)
async def get_all_predictions(
    image: UploadFile = File(...),
    top_k: int = 5
):
    """
    Get multiple disease predictions for an image.
    
    Args:
        image: Uploaded image file
        top_k: Number of top predictions to return
        
    Returns:
        List of predictions with confidence scores
    """
    try:
        # Validate
        if not validate_image_type(
            image.content_type,
            settings.ALLOWED_IMAGE_TYPES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type"
            )
        
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        predictions = await disease_service.get_all_predictions(
            image_bytes,
            top_k=min(top_k, 10)  # Cap at 10
        )
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get predictions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
