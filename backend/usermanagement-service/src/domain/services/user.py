import structlog
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings as app_settings
from src.domain.contracts import UserOperations, UserRegister
from src.domain.models.user import User
from src.domain.schemas.user import (
    Login2FAResponse,
    LoginRequest,
    LoginResponse,
    LoginResult,
    UserProfileUpdateRequest,
    UserRegisterRequest,
    UserResponse,
    Verify2FARequest,
)
from src.domain.services.commands.get_paginated_users import (
    GetPaginatedUserProfilesCommand,
)
from src.domain.services.commands.get_user_profile import GetUserProfileCommand
from src.domain.services.commands.github_oauth import GithubOAuthCommand
from src.domain.services.commands.login_user import LoginCommand
from src.domain.services.commands.register_user import RegisterUserCommand
from src.domain.services.commands.update_user_profile import UpdateUserProfileCommand
from src.domain.services.commands.verify_two_factor import VerifyTwoFactorCommand
from src.domain.services.otp import OtpService
from src.domain.services.password import PasswordService
from src.domain.services.token import TokenService
from src.infrastructure.event_publisher import EventPublisher

logger = structlog.get_logger()

EMAIL_WELCOME_CHANNEL = "email:welcome"
EMAIL_OTP_CHANNEL = "email:otp"


class UserService(UserRegister, UserOperations):
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
        logger.info("Sending welcome email", user_id=user.id)
        await self.send_welcome_email(user.email, user.username)
        return user

    async def get_user_profile(self, user_id: str):
        command = GetUserProfileCommand(self.session, user_id)
        return await command.execute()

    async def get_paginated_user_profiles(self, page: int = 1, page_size: int = 10):
        command = GetPaginatedUserProfilesCommand(self.session, page, page_size)
        return await command.execute()

    async def update_user_profile(
        self, user_id: str, payload: UserProfileUpdateRequest
    ):
        command = UpdateUserProfileCommand(self.session, user_id, payload)
        return await command.execute()

    # Messaging methods
    async def send_welcome_email(self, email: str, username: str) -> None:
        await self.event_publisher.publish(
            EMAIL_WELCOME_CHANNEL,
            {"email": email, "username": username},
        )

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

    async def verify_two_factor(self, payload: Verify2FARequest) -> LoginResponse:
        command = VerifyTwoFactorCommand(
            token_service=self.token_service,
            otp_service=self.otp_service,
            payload=payload,
        )
        result = await command.execute()

        user = await self.get_user_profile(result["user_id"])
        logger.info("2FA login completed", user_id=result["user_id"])

        return LoginResponse(
            access_token=result["access_token"],
            user=UserResponse.model_validate(user),
        )

    async def github_oauth_login(self, code: str) -> LoginResponse:
        command = GithubOAuthCommand(
            session=self.session,
            token_service=self.token_service,
            settings=app_settings,
            code=code,
        )
        result = await command.execute()
        return LoginResponse(
            access_token=result["token"],
            user=UserResponse.model_validate(result["user"]),
        )
