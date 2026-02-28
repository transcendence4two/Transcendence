from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import InvalidCredentialsError
from src.domain.models.user import User
from src.domain.schemas.user import LoginRequest
from src.domain.services.commands.base import Command
from src.domain.services.otp import OtpService
from src.domain.services.password import PasswordService
from src.domain.services.token import TokenService
from src.infrastructure.event_publisher import EventPublisher

logger = structlog.get_logger()

EMAIL_OTP_CHANNEL = "email:otp"
TEMPORARY_TOKEN_EXPIRATION = 5  # minutes


class LoginCommand(Command):
    """Command to authenticate a user and handle login flow."""

    def __init__(
        self,
        session: AsyncSession,
        password_service: PasswordService,
        token_service: TokenService,
        otp_service: OtpService,
        event_publisher: EventPublisher,
        payload: LoginRequest,
    ):
        self.session = session
        self.password_service = password_service
        self.token_service = token_service
        self.otp_service = otp_service
        self.event_publisher = event_publisher
        self.payload = payload

    async def execute(self) -> dict[str, Any]:
        """Execute login authentication"""
        user = await self._authenticate_user()

        logger.info(
            "User authenticated",
            user_id=user.id,
            two_fa_enabled=user.enable_2fa,
        )

        if user.enable_2fa:
            return await self._handle_2fa_flow(user)

        return await self._handle_normal_login(user)

    async def _authenticate_user(self) -> User:
        """Authenticate user credentials"""
        stmt = select(User).where(User.email == self.payload.email)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            logger.warning("Login attempt with non-existent email")
            raise InvalidCredentialsError("Email ou senha incorretos")

        if not self.password_service.verify_password(
            self.payload.password, user.hashed_password
        ):
            logger.warning("Failed login attempt", user_id=user.id)
            raise InvalidCredentialsError("Email ou senha incorretos")

        logger.info("User credentials validated", user_id=user.id)
        return user

    async def _handle_normal_login(self, user: User) -> dict[str, Any]:
        """Handle login for users without 2FA enabled"""
        access_token = self.token_service.create_token(user.id)
        logger.info("Normal login completed", user_id=user.id)

        return {
            "token": access_token,
            "user": user,
            "requires_2fa": False,
        }

    async def _handle_2fa_flow(self, user: User) -> dict[str, Any]:
        """Handle login for users with 2FA enabled"""
        logger.info("Handling 2FA flow", user_id=user.id)

        temporary_token = self.token_service.create_token(
            user.id, expires_minutes=TEMPORARY_TOKEN_EXPIRATION
        )

        otp_code = self.otp_service.generate_otp()

        await self.otp_service.store_otp(user.id, otp_code)
        logger.info("OTP code stored", user_id=user.id)

        event_data = {
            "email": user.email,
            "username": user.username,
            "otp_code": otp_code,
        }

        await self.event_publisher.publish(EMAIL_OTP_CHANNEL, event_data)

        logger.info("2FA flow completed", user_id=user.id)

        return {
            "temporary_token": temporary_token,
            "requires_2fa": True,
        }
