"""
Configuration package initialization.
Exports settings for easy import across the application.
"""

from .settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
