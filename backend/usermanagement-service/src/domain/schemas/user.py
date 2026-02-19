from typing import Literal, Union

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


class LoginRequest(BaseModel):
    """Schema for user login request"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=255)


class LoginResponse(BaseModel):
    """Schema for successful login response without 2FA"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class Login2FAResponse(BaseModel):
    """Schema for login response when 2FA is required"""

    temporary_token: str
    twofa_required: bool = Field(default=True, alias="2fa_required")
    message: str

    class Config:
        populate_by_name = True


class LoginResult(BaseModel):
    """Internal result from login service"""

    requires_2fa: bool
    response: Union[LoginResponse, Login2FAResponse]
    status_code: int
