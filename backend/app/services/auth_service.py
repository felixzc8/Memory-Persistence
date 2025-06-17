from supabase import create_client, Client
from typing import Optional, Dict, Any
from app.config import settings
from app.schemas.auth import UserResponse, AuthResponse
import logging
from datetime import datetime
import jwt

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling Supabase authentication operations"""
    
    def __init__(self):
        try:
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("Supabase auth service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase auth service: {e}")
            raise
    
    async def sign_up(self, email: str, password: str, full_name: Optional[str] = None) -> AuthResponse:
        """
        Register a new user with Supabase Auth
        
        Args:
            email: User's email address
            password: User's password
            full_name: Optional full name
            
        Returns:
            AuthResponse with user data and tokens
        """
        try:
            # Prepare user metadata
            user_metadata = {}
            if full_name:
                user_metadata["full_name"] = full_name
            
            # Sign up with Supabase
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            if not auth_response.user or not auth_response.session:
                raise Exception("Failed to create user account")
            
            user_data = self._format_user_response(auth_response.user)
            
            return AuthResponse(
                user=user_data,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                expires_in=auth_response.session.expires_in or 3600,
                token_type="bearer"
            )
            
        except Exception as e:
            logger.error(f"Error during sign up: {e}")
            raise Exception(f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> AuthResponse:
        """
        Sign in an existing user
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            AuthResponse with user data and tokens
        """
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user or not auth_response.session:
                raise Exception("Invalid credentials")
            
            user_data = self._format_user_response(auth_response.user)
            
            return AuthResponse(
                user=user_data,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                expires_in=auth_response.session.expires_in or 3600,
                token_type="bearer"
            )
            
        except Exception as e:
            logger.error(f"Error during sign in: {e}")
            raise Exception(f"Sign in failed: {str(e)}")
    
    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out a user
        
        Args:
            access_token: User's access token
            
        Returns:
            True if successful
        """
        try:
            # Set the session for the client
            self.supabase.auth.set_session(access_token, "")
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Error during sign out: {e}")
            return False
    
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh an access token
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            AuthResponse with new tokens
        """
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.user or not auth_response.session:
                raise Exception("Failed to refresh token")
            
            user_data = self._format_user_response(auth_response.user)
            
            return AuthResponse(
                user=user_data,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
                expires_in=auth_response.session.expires_in or 3600,
                token_type="bearer"
            )
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise Exception(f"Token refresh failed: {str(e)}")
    
    async def get_user_from_token(self, access_token: str) -> Optional[UserResponse]:
        """
        Get user information from access token
        
        Args:
            access_token: JWT access token
            
        Returns:
            UserResponse if token is valid, None otherwise
        """
        try:
            # Set the session and get user
            self.supabase.auth.set_session(access_token, "")
            user_response = self.supabase.auth.get_user()
            
            if not user_response.user:
                return None
            
            return self._format_user_response(user_response.user)
            
        except Exception as e:
            logger.error(f"Error getting user from token: {e}")
            return None
    
    async def update_user_profile(self, access_token: str, updates: Dict[str, Any]) -> UserResponse:
        """
        Update user profile
        
        Args:
            access_token: User's access token
            updates: Dictionary of fields to update
            
        Returns:
            Updated UserResponse
        """
        try:
            self.supabase.auth.set_session(access_token, "")
            
            # Format updates for Supabase
            user_attributes = {}
            if "email" in updates:
                user_attributes["email"] = updates["email"]
            
            # Handle metadata updates
            if "full_name" in updates:
                user_attributes["data"] = {"full_name": updates["full_name"]}
            
            auth_response = self.supabase.auth.update_user(user_attributes)
            
            if not auth_response.user:
                raise Exception("Failed to update user profile")
            
            return self._format_user_response(auth_response.user)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise Exception(f"Profile update failed: {str(e)}")
    
    async def change_password(self, access_token: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            access_token: User's access token
            new_password: New password
            
        Returns:
            True if successful
        """
        try:
            self.supabase.auth.set_session(access_token, "")
            auth_response = self.supabase.auth.update_user({"password": new_password})
            
            return auth_response.user is not None
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
    
    async def reset_password(self, email: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            
        Returns:
            True if email was sent successfully
        """
        try:
            self.supabase.auth.reset_password_email(email)
            return True
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    def _format_user_response(self, user) -> UserResponse:
        """Format Supabase user object to UserResponse"""
        return UserResponse(
            id=user.id,
            email=user.email or "",
            full_name=user.user_metadata.get("full_name") if user.user_metadata else None,
            email_confirmed_at=datetime.fromisoformat(user.email_confirmed_at.replace('Z', '+00:00')) if user.email_confirmed_at else None,
            created_at=datetime.fromisoformat(user.created_at.replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user.updated_at.replace('Z', '+00:00'))
        )

# Singleton instance
auth_service = AuthService() 