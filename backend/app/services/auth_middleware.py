from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from supabase import create_client, Client
from app.config import settings
import logging
import jwt

logger = logging.getLogger(__name__)

# Simple UserResponse model for auth middleware
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    email_confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# HTTP Bearer token security scheme
security = HTTPBearer()

# Initialize Supabase client for JWT verification
try:
    supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
    logger.info("Supabase client initialized for auth middleware")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

def _format_user_response(user) -> UserResponse:
    """Format Supabase user object to UserResponse"""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.user_metadata.get("full_name") if user.user_metadata else None,
        email_confirmed_at=datetime.fromisoformat(user.email_confirmed_at.replace('Z', '+00:00')) if user.email_confirmed_at else None,
        created_at=datetime.fromisoformat(user.created_at.replace('Z', '+00:00')),
        updated_at=datetime.fromisoformat(user.updated_at.replace('Z', '+00:00'))
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    Dependency to get the current authenticated user from Supabase JWT token
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        UserResponse: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )
    
    try:
        token = credentials.credentials
        
        # Validate JWT token locally for better performance
        try:
            # Decode and validate the JWT token
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,  # Use the JWT secret from settings
                algorithms=["HS256"],
                audience="authenticated"
            )
            
            # Extract user information from the JWT payload
            user_id = payload.get("sub")
            email = payload.get("email") 
            user_metadata = payload.get("user_metadata", {})
            
            if not user_id or not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create user response from JWT payload
            return UserResponse(
                id=user_id,
                email=email,
                full_name=user_metadata.get("full_name"),
                email_confirmed_at=datetime.fromisoformat(payload.get("email_confirmed_at", "").replace('Z', '+00:00')) if payload.get("email_confirmed_at") else None,
                created_at=datetime.fromisoformat(payload.get("created_at", datetime.now().isoformat()).replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(payload.get("updated_at", datetime.now().isoformat()).replace('Z', '+00:00'))
            )
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
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
    if not credentials or not supabase:
        return None
    
    try:
        token = credentials.credentials
        supabase.auth.set_session(token, "")
        user_response = supabase.auth.get_user()
        
        if user_response.user:
            return _format_user_response(user_response.user)
        return None
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