"""
Disease Detection Service
Handles plant disease identification using HuggingFace Inference API.
"""

import httpx
from typing import Tuple, List, Optional
from loguru import logger

from config.settings import settings
from utils.helpers import format_disease_name


class DiseaseDetectionService:
    """
    Service for detecting plant diseases from images using HuggingFace models.
    """
    
    def __init__(self):
        """Initialize the disease detection service with API configuration."""
        self.api_url = settings.HUGGINGFACE_MODEL_URL
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/octet-stream"
        }
        
        # Check if API key is configured
        self.demo_mode = (
            not self.api_key or 
            self.api_key == "your_huggingface_api_key_here" or
            len(self.api_key) < 10
        )
        
        if self.demo_mode:
            logger.warning("HuggingFace API key not configured - running in demo mode")
        
        # Demo diseases for simulation
        self.demo_diseases = [
            ("Tomato Late Blight", 0.92, "late_blight"),
            ("Tomato Early Blight", 0.88, "early_blight"),
            ("Tomato Leaf Spot", 0.85, "leaf_spot"),
            ("Healthy Plant", 0.95, "healthy"),
            ("Powdery Mildew", 0.87, "powdery_mildew"),
        ]
        
        # Disease treatment recommendations database
        self.treatment_database = {
            "late_blight": [
                "Remove and destroy infected plant parts immediately",
                "Apply copper-based fungicide (Bordeaux mixture)",
                "Ensure proper spacing for air circulation",
                "Avoid overhead irrigation",
                "Rotate crops annually"
            ],
            "early_blight": [
                "Remove infected lower leaves",
                "Apply chlorothalonil or mancozeb fungicide",
                "Mulch around plants to prevent soil splash",
                "Water at the base of plants",
                "Maintain proper plant nutrition"
            ],
            "powdery_mildew": [
                "Apply sulfur-based fungicide",
                "Improve air circulation",
                "Avoid overhead watering",
                "Remove severely infected leaves",
                "Apply neem oil as organic alternative"
            ],
            "leaf_spot": [
                "Remove infected leaves",
                "Apply copper fungicide",
                "Avoid wetting foliage",
                "Ensure proper drainage",
                "Practice crop rotation"
            ],
            "bacterial_spot": [
                "Remove infected plant material",
                "Apply copper-based bactericide",
                "Avoid working with wet plants",
                "Use disease-free seeds",
                "Sanitize tools regularly"
            ],
            "healthy": [
                "Continue regular watering schedule",
                "Maintain balanced fertilization",
                "Monitor for any signs of stress",
                "Ensure proper sunlight exposure",
                "Keep area weed-free"
            ],
            "default": [
                "Consult local agricultural extension office",
                "Take multiple photos for better diagnosis",
                "Isolate affected plants if possible",
                "Maintain good garden hygiene",
                "Consider soil testing"
            ]
        }
    
    async def detect_disease(self, image_bytes: bytes) -> Tuple[str, float, List[str]]:
        """
        Detect plant disease from image bytes.
        
        Args:
            image_bytes: Raw image data as bytes
            
        Returns:
            Tuple of (disease_name, confidence_score, recommendations)
        """
        try:
            logger.info("Starting disease detection...")
            
            # Return demo response if API key not configured
            if self.demo_mode:
                import random
                demo = random.choice(self.demo_diseases)
                disease_name, confidence, disease_key = demo
                recommendations = self._get_recommendations(disease_key)
                recommendations.append("Note: This is a demo result. Configure HUGGINGFACE_API_KEY for real disease detection.")
                logger.info(f"Demo mode - returning: {disease_name}")
                return disease_name, confidence, recommendations
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    content=image_bytes
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if results and len(results) > 0:
                        # Get top prediction
                        top_result = results[0]
                        disease_raw = top_result.get("label", "Unknown")
                        confidence = top_result.get("score", 0.0)
                        
                        # Format disease name
                        disease = format_disease_name(disease_raw)
                        
                        # Get recommendations
                        recommendations = self._get_recommendations(disease_raw)
                        
                        logger.info(
                            f"Disease detected: {disease} "
                            f"(confidence: {confidence:.2%})"
                        )
                        
                        return disease, confidence, recommendations
                    else:
                        logger.warning("No predictions returned from model")
                        return "Unknown", 0.0, self.treatment_database["default"]
                        
                elif response.status_code == 503:
                    logger.warning("Model is loading, please retry")
                    raise Exception("Model is loading. Please try again in a few seconds.")
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error: {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error("Request timeout during disease detection")
            raise Exception("Request timeout. Please try again.")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception("Network error. Please check your connection.")
        except Exception as e:
            logger.error(f"Disease detection error: {e}")
            raise
    
    def _get_recommendations(self, disease_name: str) -> List[str]:
        """
        Get treatment recommendations based on disease name.
        
        Args:
            disease_name: Raw disease name from model
            
        Returns:
            List of treatment recommendations
        """
        disease_lower = disease_name.lower()
        
        # Check for matching keywords in disease name
        for key, recommendations in self.treatment_database.items():
            if key in disease_lower:
                return recommendations
        
        # Check if plant is healthy
        if "healthy" in disease_lower:
            return self.treatment_database["healthy"]
        
        # Return default recommendations
        return self.treatment_database["default"]
    
    async def get_all_predictions(
        self, 
        image_bytes: bytes, 
        top_k: int = 5
    ) -> List[dict]:
        """
        Get top-k disease predictions with confidence scores.
        
        Args:
            image_bytes: Raw image data
            top_k: Number of top predictions to return
            
        Returns:
            List of prediction dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    content=image_bytes
                )
                
                if response.status_code == 200:
                    results = response.json()
                    predictions = []
                    
                    for result in results[:top_k]:
                        predictions.append({
                            "disease": format_disease_name(result.get("label", "")),
                            "confidence": result.get("score", 0.0),
                            "raw_label": result.get("label", "")
                        })
                    
                    return predictions
                else:
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting all predictions: {e}")
            raise


# Singleton instance
disease_service = DiseaseDetectionService()
