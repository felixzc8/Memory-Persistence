from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserSignUp(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (minimum 6 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")

class UserSignIn(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class UserResponse(BaseModel):
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    email_confirmed_at: Optional[datetime] = Field(None, description="Email confirmation timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class AuthResponse(BaseModel):
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(default="bearer", description="Token type")

class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")

class ChangePassword(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password (minimum 6 characters)")

class ResetPassword(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")

class UpdateProfile(BaseModel):
    full_name: Optional[str] = Field(None, description="Updated full name")
    email: Optional[EmailStr] = Field(None, description="Updated email address")

class AuthError(BaseModel):
    error: str = Field(..., description="Error message")
    message: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code") 