from fastapi import APIRouter, Depends, status

from src.core.auth import get_token_payload, verify_user_authorization
from src.di_config import get_token_service, get_user_service
from src.domain.contracts import TokenProvider
from src.domain.schemas.user import (
    Toggle2FARequest,
    TokenRequest,
    TokenResponse,
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


###


@router.get("/protected")
async def protected_route(payload: dict = Depends(get_token_payload)):
    return {"message": "authenticated", "sub": payload.get("sub")}


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
