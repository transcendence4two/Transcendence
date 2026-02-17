from datetime import datetime
from typing import Generic, TypeVar

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


class UserProfileUpdateRequest(BaseModel):
    """Schema for user profile update"""

    username: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None


class Toggle2FARequest(BaseModel):
    """Schema for toggling 2FA"""

    enable: bool


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


### To be removed
class TokenRequest(BaseModel):
    """Schema for token generation request"""

    user_id: str = Field(..., min_length=1, description="User ID for token subject")


class TokenResponse(BaseModel):
    """Schema for token generation response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


###
