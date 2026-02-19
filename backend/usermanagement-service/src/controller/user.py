from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.core.auth import get_token_payload
from src.di_config import get_user_service
from src.domain.schemas.user import (
    Login2FAResponse,
    LoginRequest,
    LoginResponse,
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
    user_service: UserService = Depends(get_user_service),
):
    """
    Authenticate user with email and password.

    Returns:
        - 200 OK with access token for users without 2FA
        - 202 Accepted with temporary token for users with 2FA enabled
    """
    result = await user_service.login_user(request)

    if result["requires_2fa"]:
        response = Login2FAResponse(
            temporary_token=result["temporary_token"],
            message="Código de verificação enviado para seu email",
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=response.model_dump(by_alias=True),
        )

    response = LoginResponse(
        access_token=result["token"],
        user=UserResponse.model_validate(result["user"]),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(),
    )


@router.get("/protected")
async def protected_route(payload: dict = Depends(get_token_payload)):
    return {"message": "authenticated", "sub": payload.get("sub")}
