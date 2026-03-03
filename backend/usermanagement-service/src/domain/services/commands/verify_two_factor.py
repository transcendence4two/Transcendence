from typing import Any

import structlog

from src.domain.exceptions import InvalidOtpError
from src.domain.schemas.user import Verify2FARequest
from src.domain.services.commands.base import Command
from src.domain.services.otp import OtpService
from src.domain.services.token import TokenService

logger = structlog.get_logger()


class VerifyTwoFactorCommand(Command):
    """Command to verify 2FA OTP code and complete login flow."""

    def __init__(
        self,
        token_service: TokenService,
        otp_service: OtpService,
        payload: Verify2FARequest,
    ):
        self.token_service = token_service
        self.otp_service = otp_service
        self.payload = payload

    async def execute(self) -> dict[str, Any]:
        user_id = self._validate_temporary_token()

        await self._verify_otp(user_id)

        access_token = self.token_service.create_token(user_id)
        logger.info("2FA verification completed", user_id=user_id)

        return {
            "access_token": access_token,
            "user_id": user_id,
        }

    def _validate_temporary_token(self) -> str:
        payload = self.token_service.validate_token(self.payload.temporary_token)
        user_id = payload["sub"]
        logger.info("Temporary token validated", user_id=user_id)
        return user_id

    async def _verify_otp(self, user_id: str) -> None:
        is_valid = await self.otp_service.verify_otp(user_id, self.payload.otp_code)

        if not is_valid:
            logger.warning("Invalid OTP attempt", user_id=user_id)
            raise InvalidOtpError("Código de verificação inválido ou expirado")

        logger.info("OTP verified successfully", user_id=user_id)
