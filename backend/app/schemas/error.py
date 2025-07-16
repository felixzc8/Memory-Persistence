"""
Error response schemas for consistent API error handling.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response schema for all API endpoints."""
    
    error_code: str = Field(..., description="Unique error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context and details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error occurrence timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors."""
    
    error_code: str = Field(default="VALIDATION_ERROR", description="Validation error code")
    field_errors: Optional[Dict[str, str]] = Field(None, description="Field-specific validation errors")


class DatabaseErrorResponse(ErrorResponse):
    """Specialized error response for database errors."""
    
    error_code: str = Field(default="DATABASE_ERROR", description="Database error code")
    operation: Optional[str] = Field(None, description="Database operation that failed")


class ChatErrorResponse(ErrorResponse):
    """Specialized error response for chat-related errors."""
    
    error_code: str = Field(default="CHAT_ERROR", description="Chat error code")
    service: Optional[str] = Field(None, description="Service that encountered the error")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    user_id: Optional[str] = Field(None, description="User ID if applicable")