from uuid import uuid4

import pytest

from src.domain.exceptions import InvalidOtpError
from src.domain.schemas.user import Verify2FARequest
from src.domain.services.commands.verify_two_factor import VerifyTwoFactorCommand


class MockTokenService:
    def __init__(self, user_id: str = "test-user-id", should_fail: bool = False):
        self.user_id = user_id
        self.should_fail = should_fail

    def create_token(self, subject: str, expires_minutes: int | None = None) -> str:
        return f"access_token_{subject}"

    def validate_token(self, token: str) -> dict:
        if self.should_fail:
            from src.domain.exceptions import TokenInvalidError

            raise TokenInvalidError("Token is invalid or verification failed")
        return {"sub": self.user_id, "iss": "test", "iat": 0, "exp": 9999999999}


class MockOtpService:
    def __init__(self, should_verify: bool = True):
        self.should_verify = should_verify

    async def verify_otp(self, user_id: str, otp: str) -> bool:
        return self.should_verify


@pytest.fixture
def user_id():
    return str(uuid4())


@pytest.fixture
def valid_payload():
    return Verify2FARequest(
        temporary_token="valid_temp_token",
        otp_code="123456",
    )


@pytest.mark.asyncio
class TestVerifyTwoFactorCommand:
    async def test_verify_2fa_success(self, user_id, valid_payload):
        """Should return access_token when token and OTP are valid."""
        # Arrange
        token_service = MockTokenService(user_id=user_id)
        otp_service = MockOtpService(should_verify=True)

        command = VerifyTwoFactorCommand(
            token_service=token_service,
            otp_service=otp_service,
            payload=valid_payload,
        )

        # Act
        result = await command.execute()

        # Assert
        assert result["access_token"] == f"access_token_{user_id}"
        assert result["user_id"] == user_id

    async def test_verify_2fa_invalid_otp(self, user_id, valid_payload):
        """Should raise InvalidOtpError when OTP code is wrong."""
        # Arrange
        token_service = MockTokenService(user_id=user_id)
        otp_service = MockOtpService(should_verify=False)

        command = VerifyTwoFactorCommand(
            token_service=token_service,
            otp_service=otp_service,
            payload=valid_payload,
        )

        # Act & Assert
        with pytest.raises(InvalidOtpError) as exc_info:
            await command.execute()

        assert "inválido ou expirado" in str(exc_info.value)

    async def test_verify_2fa_invalid_token(self, valid_payload):
        """Should raise TokenInvalidError when temporary token is invalid."""
        # Arrange
        from src.domain.exceptions import TokenInvalidError

        token_service = MockTokenService(should_fail=True)
        otp_service = MockOtpService(should_verify=True)

        command = VerifyTwoFactorCommand(
            token_service=token_service,
            otp_service=otp_service,
            payload=valid_payload,
        )

        # Act & Assert
        with pytest.raises(TokenInvalidError):
            await command.execute()

    async def test_verify_2fa_expired_token(self, valid_payload):
        """Should raise TokenExpiredError when temporary token is expired."""
        # Arrange
        from src.domain.exceptions import TokenExpiredError

        class ExpiredTokenService:
            def validate_token(self, token: str) -> dict:
                raise TokenExpiredError("Token has expired")

            def create_token(self, subject: str, expires_minutes: int | None = None):
                return f"token_{subject}"

        token_service = ExpiredTokenService()
        otp_service = MockOtpService(should_verify=True)

        command = VerifyTwoFactorCommand(
            token_service=token_service,
            otp_service=otp_service,
            payload=valid_payload,
        )

        # Act & Assert
        with pytest.raises(TokenExpiredError):
            await command.execute()
