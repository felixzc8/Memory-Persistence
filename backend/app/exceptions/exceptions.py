"""
Custom exceptions for the chatbot application.

This module defines domain-specific exceptions that provide better error handling
and more meaningful error messages throughout the application.
"""

from typing import Optional, Dict, Any


class DatabaseException(Exception):
    """Exception for database-related errors including TiDB connection, session, and user storage issues."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "DATABASE_ERROR"
        self.details = details or {}


class ValidationException(Exception):
    """Exception for validation errors including user ID mismatches, session ownership, and invalid inputs."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "VALIDATION_ERROR"
        self.details = details or {}


class ChatException(Exception):
    """Exception for chat-related errors including OpenAI API failures, memory service issues, and chat processing problems."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CHAT_ERROR"
        self.details = details or {}