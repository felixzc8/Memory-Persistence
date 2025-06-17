from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import auth_service
from app.schemas.auth import UserResponse
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        UserResponse: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        user = await auth_service.get_user_from_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserResponse]:
    """
    Optional dependency to get the current user (doesn't raise error if no token)
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        Optional[UserResponse]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.get_user_from_token(token)
        return user
    except Exception as e:
        logger.error(f"Error in get_current_user_optional: {e}")
        return None

def require_auth(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Dependency that requires authentication
    
    Args:
        user: Current authenticated user
        
    Returns:
        UserResponse: The authenticated user
    """
    return user

def optional_auth(user: Optional[UserResponse] = Depends(get_current_user_optional)) -> Optional[UserResponse]:
    """
    Dependency for optional authentication
    
    Args:
        user: Current user if authenticated
        
    Returns:
        Optional[UserResponse]: The user if authenticated, None otherwise
    """
    return user 