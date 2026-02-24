from fastapi import APIRouter, Depends, Query, Response, status

from src.core.auth import get_token_payload
from src.di_config import get_user_service
from src.domain.schemas.user import (
    LoginRequest,
    PaginatedResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
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
    user = await user_service.update_user_profile(user_id, request)
    return UserProfileResponse.model_validate(user)
