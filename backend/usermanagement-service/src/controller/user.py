from fastapi import APIRouter, Depends, Response, status

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
