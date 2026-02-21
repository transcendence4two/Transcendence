from fastapi import APIRouter, Depends, Response, Query, status

from src.core.auth import get_token_payload, verify_user_authorization
from src.di_config import get_token_service, get_user_service
from src.domain.contracts import TokenProvider
from src.domain.schemas.user import (
    PaginatedResponse,
    Toggle2FARequest,
    TokenRequest,
    TokenResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from src.core.auth import get_token_payload
from src.di_config import get_user_service
from src.domain.schemas.user import (
    LoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.domain.services.user import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.register_user(request)
    return UserResponse.model_validate(user)


### to be removed
@router.post("/token", response_model=TokenResponse)
async def generate_token(
    request: TokenRequest,
    token_service: TokenProvider = Depends(get_token_service),
):
    """Generate JWT token for testing purposes"""
    token = token_service.create_token(request.user_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=60,
    )


@router.post("/login")
async def login_user(
    request: LoginRequest,
    response: Response,
    user_service: UserService = Depends(get_user_service),
):
    """Authenticate user with email and password."""
    result = await user_service.login_user(request)
    response.status_code = result.status_code
    return result.response


@router.get("/protected")
async def protected_route(payload: dict = Depends(get_token_payload)):
    return {"message": "authenticated", "sub": payload.get("sub")}


@router.get("/", response_model=PaginatedResponse[UserProfileResponse])
async def get_all_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    result = await user_service.get_paginated_user_profiles(page, page_size)
    return result


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(
    user_id: str,
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_profile(user_id)
    return UserProfileResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_profile(
    user_id: str,
    request: UserProfileUpdateRequest,
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    verify_user_authorization(user_id, payload)
    user = await user_service.update_user_profile(user_id, request)
    return UserProfileResponse.model_validate(user)


@router.put("/toggle-2fa", response_model=UserProfileResponse)
async def toggle_2fa(
    request: Toggle2FARequest,
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    user_id = payload.get("sub")
    user = await user_service.toggle_2fa(user_id, request.enable)
    return UserProfileResponse.model_validate(user)
