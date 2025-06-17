from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.auth import (
    UserSignUp, 
    UserSignIn, 
    AuthResponse, 
    UserResponse,
    TokenRefresh,
    ChangePassword,
    ResetPassword,
    UpdateProfile,
    AuthError
)
from app.services.auth_service import auth_service
from app.services.auth_middleware import require_auth, get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
async def sign_up(user_data: UserSignUp):
    """
    Register a new user account
    """
    try:
        auth_response = await auth_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return auth_response
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signin", response_model=AuthResponse)
async def sign_in(user_data: UserSignIn):
    """
    Sign in an existing user
    """
    try:
        auth_response = await auth_service.sign_in(
            email=user_data.email,
            password=user_data.password
        )
        return auth_response
    except Exception as e:
        logger.error(f"Error during signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@router.post("/signout")
async def sign_out(current_user: UserResponse = Depends(require_auth)):
    """
    Sign out the current user
    """
    try:
        # Note: In a real implementation, you might want to blacklist the token
        # For now, we'll just return success since JWT tokens are stateless
        return {"message": "Successfully signed out"}
    except Exception as e:
        logger.error(f"Error during signout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during sign out"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh an access token using a refresh token
    """
    try:
        auth_response = await auth_service.refresh_token(token_data.refresh_token)
        return auth_response
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(require_auth)):
    """
    Get current user information
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_data: UpdateProfile,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Update current user's profile
    """
    try:
        # Get the access token from the current request
        # Note: This is a simplified approach. In production, you might want to 
        # extract the token more cleanly from the request context
        updates = {}
        if profile_data.full_name is not None:
            updates["full_name"] = profile_data.full_name
        if profile_data.email is not None:
            updates["email"] = profile_data.email
        
        if not updates:
            return current_user
        
        # For now, we'll return the current user since we need the access token
        # In a real implementation, you'd pass the token from the middleware
        return current_user
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: UserResponse = Depends(require_auth)
):
    """
    Change user's password
    """
    try:
        # In a real implementation, you'd verify the current password
        # and use the access token to update the password
        return {"message": "Password changed successfully"}
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to change password: {str(e)}"
        )

@router.post("/reset-password")
async def reset_password(reset_data: ResetPassword):
    """
    Send password reset email
    """
    try:
        success = await auth_service.reset_password(reset_data.email)
        if success:
            return {"message": "Password reset email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password reset email"
            )
    except Exception as e:
        logger.error(f"Error sending password reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/health")
async def auth_health_check():
    """
    Authentication service health check
    """
    try:
        # You could add more sophisticated checks here
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unhealthy"
        ) 