from typing import Any

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.contracts import UserRegister
from src.domain.models.user import User
from src.domain.schemas.user import (
    Login2FAResponse,
    LoginRequest,
    LoginResponse,
    LoginResult,
    UserRegisterRequest,
    UserResponse,
)
from src.domain.services.commands.login_user import LoginCommand
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.otp import OtpService
from src.domain.services.password import PasswordService
from src.domain.services.token import TokenService
from src.infrastructure.event_publisher import EventPublisher

EMAIL_WELCOME_CHANNEL = "email:welcome"
EMAIL_OTP_CHANNEL = "email:otp"


class UserService(UserRegister):
    """Service for user operations"""

    def __init__(
        self,
        session: AsyncSession,
        password_service: PasswordService,
        token_service: TokenService,
        otp_service: OtpService,
        event_publisher: EventPublisher,
    ):
        self.session = session
        self.password_service = password_service
        self.token_service = token_service
        self.otp_service = otp_service
        self.event_publisher = event_publisher

    async def register_user(self, payload: UserRegisterRequest):
        command = RegisterUserCommand(
            session=self.session,
            password_service=self.password_service,
            payload=payload,
        )
        user = await command.execute()
        await self.event_publisher.publish(
            EMAIL_WELCOME_CHANNEL,
            {"email": user.email, "username": user.username},
        )
        return user

    async def send_otp_email(self, email: str, otp_code: str) -> None:
        await self.event_publisher.publish(
            EMAIL_OTP_CHANNEL,
            {"email": email, "otp_code": otp_code},
        )

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def login_user(self, payload: LoginRequest) -> LoginResult:
        """Authenticate user and handle login flow"""
        command = LoginCommand(
            session=self.session,
            password_service=self.password_service,
            token_service=self.token_service,
            otp_service=self.otp_service,
            event_publisher=self.event_publisher,
            payload=payload,
        )
        result = await command.execute()

        if result["requires_2fa"]:
            response = Login2FAResponse(
                temporary_token=result["temporary_token"],
                message="Código de verificação enviado para seu email",
            )
            return LoginResult(
                requires_2fa=True,
                response=response,
                status_code=status.HTTP_202_ACCEPTED,
            )

        response = LoginResponse(
            access_token=result["token"],
            user=UserResponse.model_validate(result["user"]),
        )
        return LoginResult(
            requires_2fa=False,
            response=response,
            status_code=status.HTTP_200_OK,
        )
