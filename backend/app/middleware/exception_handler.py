"""
Global exception handler middleware for standardized error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.exceptions import DatabaseException, ValidationException, ChatException
from app.schemas.error import ErrorResponse, ValidationErrorResponse, DatabaseErrorResponse, ChatErrorResponse
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """Handle database-related exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.error(f"Database error [{request_id}]: {exc.message}", extra={
        "request_id": request_id,
        "error_code": exc.error_code,
        "details": exc.details
    })
    
    response = DatabaseErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.now(),
        request_id=request_id
    )
    return JSONResponse(status_code=500, content=response.model_dump(mode='json'))


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation-related exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.warning(f"Validation error [{request_id}]: {exc.message}", extra={
        "request_id": request_id,
        "error_code": exc.error_code,
        "details": exc.details
    })
    
    status_code = 400
    if "access denied" in exc.message.lower() or "does not belong" in exc.message.lower():
        status_code = 403
    elif "not found" in exc.message.lower():
        status_code = 404
    
    response = ValidationErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.now(),
        request_id=request_id
    )
    return JSONResponse(status_code=status_code, content=response.model_dump(mode='json'))


async def chat_exception_handler(request: Request, exc: ChatException) -> JSONResponse:
    """Handle chat-related exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.error(f"Chat error [{request_id}]: {exc.message}", extra={
        "request_id": request_id,
        "error_code": exc.error_code,
        "details": exc.details
    })
    
    response = ChatErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.now(),
        request_id=request_id
    )
    return JSONResponse(status_code=500, content=response.model_dump(mode='json'))


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.warning(f"HTTP error [{request_id}]: {exc.detail}")
    
    response = ErrorResponse(
        error_code="HTTP_ERROR",
        message=exc.detail,
        timestamp=datetime.now(),
        request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode='json'))


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.error(f"Unexpected error [{request_id}]: {str(exc)}", exc_info=True)
    
    response = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        timestamp=datetime.now(),
        request_id=request_id
    )
    return JSONResponse(status_code=500, content=response.model_dump(mode='json'))