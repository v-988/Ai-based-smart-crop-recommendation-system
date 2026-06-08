"""
Backend tests for Plant Disease Detection API.
Tests all major endpoints and services.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_api_status(self, client):
        """Test API status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "features" in data
        assert "endpoints" in data


class TestDetectEndpoints:
    """Test disease detection endpoints."""
    
    def test_detect_no_file(self, client):
        """Test detect endpoint without file."""
        response = client.post("/api/v1/detect")
        assert response.status_code == 422
    
    def test_detect_invalid_file_type(self, client):
        """Test detect endpoint with invalid file type."""
        response = client.post(
            "/api/v1/detect",
            files={"image": ("test.txt", b"not an image", "text/plain")}
        )
        assert response.status_code == 400
    
    @patch('services.disease_service.disease_service.detect_disease')
    def test_detect_success(self, mock_detect, client):
        """Test successful disease detection."""
        mock_detect.return_value = (
            "Tomato Late Blight",
            0.95,
            ["Remove infected leaves", "Apply fungicide"]
        )
        
        # Create a simple test image
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            "/api/v1/detect",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "disease" in data
        assert "confidence" in data
        assert "recommendations" in data


class TestChatEndpoints:
    """Test chatbot endpoints."""
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message."""
        response = client.post(
            "/api/v1/chat",
            json={"message": ""}
        )
        assert response.status_code == 422
    
    @patch('services.llm_service.llm_service.chat')
    def test_chat_success(self, mock_chat, client):
        """Test successful chat."""
        mock_chat.return_value = "Here are some tips for treating late blight..."
        
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "How do I treat tomato blight?",
                "disease_context": "Late Blight",
                "language": "English"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "language" in data
    
    def test_get_languages(self, client):
        """Test get supported languages."""
        response = client.get("/api/v1/chat/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data


class TestVoiceEndpoints:
    """Test voice processing endpoints."""
    
    def test_transcribe_no_file(self, client):
        """Test transcribe without file."""
        response = client.post("/api/v1/voice/transcribe")
        assert response.status_code == 422
    
    def test_synthesize_empty_text(self, client):
        """Test synthesize with empty text."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={"text": "", "language": "English"}
        )
        assert response.status_code == 400
    
    def test_get_voice_languages(self, client):
        """Test get voice languages."""
        response = client.get("/api/v1/voice/languages")
        assert response.status_code == 200
        data = response.json()
        assert "tts_languages" in data
        assert "stt_languages" in data


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_clean_markdown_text(self):
        """Test markdown cleaning."""
        from utils.helpers import clean_markdown_text
        
        text = "**Bold** and *italic* text with # header"
        cleaned = clean_markdown_text(text)
        
        assert "**" not in cleaned
        assert "*" not in cleaned
        assert "#" not in cleaned
    
    def test_format_disease_name(self):
        """Test disease name formatting."""
        from utils.helpers import format_disease_name
        
        raw = "Tomato___Late_blight"
        formatted = format_disease_name(raw)
        
        assert "___" not in formatted
        assert "_" not in formatted
        assert "Late" in formatted
    
    def test_is_sentence_complete(self):
        """Test sentence completion check."""
        from utils.helpers import is_sentence_complete
        
        assert is_sentence_complete("This is complete.")
        assert is_sentence_complete("Is this a question?")
        assert not is_sentence_complete("This is incomplete")
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        from utils.helpers import generate_session_id
        
        id1 = generate_session_id()
        id2 = generate_session_id()
        
        assert id1 != id2
        assert len(id1) == 36  # UUID format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
