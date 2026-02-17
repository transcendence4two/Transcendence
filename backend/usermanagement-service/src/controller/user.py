from fastapi import APIRouter, Depends, status

from src.core.auth import get_token_payload
from src.di_config import get_user_service
from src.domain.schemas.user import (
    UserProfileResponse,
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

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(
    user_id: str,
    payload: dict = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_profile(user_id)
    return UserProfileResponse.model_validate(user)


@router.get("/protected")
async def protected_route(payload: dict = Depends(get_token_payload)):
    return {"message": "authenticated", "sub": payload.get("sub")}
