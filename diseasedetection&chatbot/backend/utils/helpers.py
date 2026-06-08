"""
Utility functions for the Plant Disease Detection API.
Contains helper functions for text processing, validation, etc.
"""

import re
import os
import uuid
from typing import Optional
from datetime import datetime
from loguru import logger


def clean_markdown_text(text: str) -> str:
    """
    Remove markdown formatting from text for cleaner voice output.
    
    Args:
        text: Text with potential markdown formatting
        
    Returns:
        Cleaned text without markdown symbols
    """
    # Remove bold markers (**text** or __text__)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # Remove remaining asterisks
    text = re.sub(r"\*+", "", text)
    # Remove italic markers (_text_)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
    # Remove headers (# ## ### etc)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    # Remove strikethrough (~~text~~)
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    # Remove inline code (`code`)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove code blocks (```code```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove image syntax ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # Remove blockquotes (> text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Clean up multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Clean up multiple spaces
    text = re.sub(r" {2,}", " ", text)
    
    return text.strip()


def generate_session_id() -> str:
    """
    Generate a unique session ID for chat history tracking.
    
    Returns:
        UUID string for session identification
    """
    return str(uuid.uuid4())


def generate_temp_filename(extension: str = ".wav") -> str:
    """
    Generate a unique temporary filename.
    
    Args:
        extension: File extension including dot
        
    Returns:
        Unique filename with timestamp and UUID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"temp_{timestamp}_{unique_id}{extension}"


def validate_image_type(content_type: Optional[str], allowed_types: str) -> bool:
    """
    Validate if the uploaded file is an allowed image type.
    
    Args:
        content_type: MIME type of uploaded file
        allowed_types: Comma-separated allowed MIME types
        
    Returns:
        True if valid, False otherwise
    """
    if not content_type:
        return False
    allowed_list = [t.strip() for t in allowed_types.split(",")]
    return content_type in allowed_list


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_disease_name(disease_name: str) -> str:
    """
    Format disease name for better readability.
    Converts 'Tomato___Late_blight' to 'Tomato - Late Blight'
    
    Args:
        disease_name: Raw disease name from model
        
    Returns:
        Formatted disease name
    """
    # Replace underscores with spaces
    formatted = disease_name.replace("___", " - ").replace("_", " ")
    # Title case each word
    formatted = " ".join(word.capitalize() for word in formatted.split())
    return formatted


def is_sentence_complete(text: str) -> bool:
    """
    Check if text ends with a complete sentence.
    
    Args:
        text: Text to check
        
    Returns:
        True if sentence appears complete
    """
    text = text.strip()
    if not text:
        return False
    
    # Check for sentence-ending punctuation
    ending_punctuation = (".", "!", "?", "।", "…")
    return text.endswith(ending_punctuation)


def cleanup_temp_files(directory: str, max_age_hours: int = 1) -> int:
    """
    Clean up old temporary files.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age of files to keep
        
    Returns:
        Number of files deleted
    """
    import time
    
    deleted_count = 0
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.debug(f"Deleted temp file: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning temp files: {e}")
    
    return deleted_count


def get_language_code(language: str) -> str:
    """
    Convert language name to ISO code.
    
    Args:
        language: Language name (English, Tamil)
        
    Returns:
        ISO language code
    """
    language_map = {
        "english": "en",
        "tamil": "ta",
        "hindi": "hi",
        "telugu": "te",
        "kannada": "kn",
        "malayalam": "ml"
    }
    return language_map.get(language.lower(), "en")


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw user input
        
    Returns:
        Sanitized text
    """
    # Remove potential HTML/script tags
    text = re.sub(r"<[^>]*>", "", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def format_confidence_score(score: float) -> str:
    """
    Format confidence score as percentage.
    
    Args:
        score: Confidence score (0-1)
        
    Returns:
        Formatted percentage string
    """
    return f"{score * 100:.1f}%"
