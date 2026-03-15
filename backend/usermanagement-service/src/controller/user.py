from fastapi import APIRouter, Depends, Query, Response, status

from src.core.auth import get_token_payload
from src.core.settings import settings
from src.di_config import get_user_service
from src.domain.exceptions import UnauthorizedActionError
from src.domain.schemas.user import (
    DeleteUserRequest,
    GithubOAuthRequest,
    LoginRequest,
    LoginResponse,
    PaginatedResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserRegisterRequest,
    UserResponse,
    Verify2FARequest,
)
from src.domain.services.user import UserService

router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"


@router.get("/oauth/github/authorize")
async def github_authorize():
    """Return the GitHub OAuth authorization URL for the frontend to redirect to."""
    params = (
        f"client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_OAUTH_REDIRECT_URI}"
        "&scope=read:user+user:email"
    )
    return {"authorize_url": f"{GITHUB_AUTHORIZE_URL}?{params}"}


@router.post("/oauth/github/callback", response_model=LoginResponse)
async def github_oauth_callback(
    request: GithubOAuthRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Exchange a GitHub OAuth code for a JWT access token."""
    return await user_service.github_oauth_login(request.code)


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


@router.post("/verify-2fa", response_model=LoginResponse)
async def verify_two_factor(
    request: Verify2FARequest,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.verify_two_factor(request)


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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    user_id: str,
    request: DeleteUserRequest,
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    if payload.get("sub") != user_id:
        raise UnauthorizedActionError("You can only delete your own user")

    await user_service.delete_user_profile(user_id, request.confirmation_text)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
