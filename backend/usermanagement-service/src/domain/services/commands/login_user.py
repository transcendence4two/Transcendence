import logging
from typing import Any

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

logger = logging.getLogger(__name__)

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
        
        logger.info(f"User {user.id} authenticated. 2FA enabled: {user.enable_2fa}")
        
        if user.enable_2fa:
            return await self._handle_2fa_flow(user)
        
        return await self._handle_normal_login(user)

    async def _authenticate_user(self) -> User:
        """Authenticate user credentials"""
        stmt = select(User).where(User.email == self.payload.email)
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            logger.warning(f"Login attempt with non-existent email: {self.payload.email}")
            raise InvalidCredentialsError("Email ou senha incorretos")

        if not self.password_service.verify_password(
            self.payload.password, user.hashed_password
        ):
            logger.warning(f"Failed login attempt for user: {user.id}")
            raise InvalidCredentialsError("Email ou senha incorretos")

        logger.info(f"User authenticated successfully: {user.id}")
        return user

    async def _handle_normal_login(self, user: User) -> dict[str, Any]:
        """Handle login for users without 2FA enabled"""
        access_token = self.token_service.create_token(user.id)
        logger.info(f"Normal login completed for user: {user.id}")
        
        return {
            "token": access_token,
            "user": user,
            "requires_2fa": False,
        }

    async def _handle_2fa_flow(self, user: User) -> dict[str, Any]:
        """Handle login for users with 2FA enabled"""
        logger.info(f"Handling 2FA flow for user: {user.id}, email: {user.email}")
        
        temporary_token = self.token_service.create_token(
            user.id, expires_minutes=TEMPORARY_TOKEN_EXPIRATION
        )
        
        otp_code = self.otp_service.generate_otp()
        logger.info(f"Generated OTP code for user {user.id}: {otp_code}")
        
        await self.otp_service.store_otp(user.id, otp_code)
        logger.info(f"OTP code stored in Redis for user {user.id}")
        
        event_data = {
            "email": user.email,
            "username": user.username,
            "otp_code": otp_code,
        }
        logger.info(f"Publishing OTP event to channel '{EMAIL_OTP_CHANNEL}' with data: {event_data}")
        
        await self.event_publisher.publish(EMAIL_OTP_CHANNEL, event_data)
        
        logger.info(f"2FA flow completed for user: {user.id}")
        
        return {
            "temporary_token": temporary_token,
            "requires_2fa": True,
        }
