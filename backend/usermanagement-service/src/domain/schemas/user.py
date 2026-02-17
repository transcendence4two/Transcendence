from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration request"""

    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)
    enable_2fa: bool = Field(default=False)


class UserResponse(BaseModel):
    """Schema for user registration response"""

    id: str
    username: str
    email: str
    enable_2fa: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""

    id: str
    username: str
    email: str
    enable_2fa: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
