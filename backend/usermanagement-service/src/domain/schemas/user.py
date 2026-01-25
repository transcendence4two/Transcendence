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
