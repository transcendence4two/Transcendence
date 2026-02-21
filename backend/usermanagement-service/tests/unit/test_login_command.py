from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import InvalidCredentialsError
from src.domain.models.user import User
from src.domain.schemas.user import LoginRequest
from src.domain.services.commands.login_user import LoginCommand


class MockPasswordService:
    """Mock password service for testing"""

    def __init__(self, should_verify: bool = True):
        self.should_verify = should_verify

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.should_verify


class MockTokenService:
    """Mock token service for testing"""

    def create_token(self, subject: str, expires_minutes: int | None = None) -> str:
        return f"token_{subject}_{expires_minutes or 60}"


class MockOtpService:
    """Mock OTP service for testing"""

    def __init__(self):
        self.stored_otps: dict[str, str] = {}

    def generate_otp(self) -> str:
        return "123456"

    async def store_otp(self, user_id: str, otp: str, ttl: int | None = None) -> None:
        self.stored_otps[user_id] = otp


class MockEventPublisher:
    """Mock event publisher for testing"""

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, channel: str, event: dict) -> None:
        self.published_events.append((channel, event))


@pytest.fixture
def mock_session():
    """Create a mock database session"""
    session = AsyncMock(spec=AsyncSession)

    # Create a properly structured mock result
    mock_scalars = Mock()
    mock_result = Mock()
    mock_result.scalars.return_value = mock_scalars

    # Make execute return the mock result directly (not a coroutine)
    async def mock_execute(*args, **kwargs):
        return mock_result

    session.execute = mock_execute
    session._mock_result = mock_result
    session._mock_scalars = mock_scalars

    return session


@pytest.fixture
def mock_user_without_2fa():
    """Create a mock user without 2FA enabled"""
    user = User(
        id=str(uuid4()),
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$hashedpassword",
        enable_2fa=False,
    )
    return user


@pytest.fixture
def mock_user_with_2fa():
    """Create a mock user with 2FA enabled"""
    user = User(
        id=str(uuid4()),
        username="user2fa",
        email="2fa@example.com",
        hashed_password="$2b$12$hashedpassword",
        enable_2fa=True,
    )
    return user


@pytest.fixture
def login_payload():
    """Create a login request payload"""
    return LoginRequest(email="test@example.com", password="password123")


@pytest.mark.asyncio
class TestLoginCommand:
    """Unit tests for LoginCommand"""

    async def test_authenticate_user_success_without_2fa(
        self, mock_session, mock_user_without_2fa, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = mock_user_without_2fa

        password_service = MockPasswordService(should_verify=True)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act
        result = await command.execute()

        # Assert
        assert result["requires_2fa"] is False
        assert "token" in result
        assert result["token"].startswith("token_")
        assert result["user"] == mock_user_without_2fa
        assert len(event_publisher.published_events) == 0

    async def test_authenticate_user_success_with_2fa(
        self, mock_session, mock_user_with_2fa, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = mock_user_with_2fa

        password_service = MockPasswordService(should_verify=True)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        login_payload.email = mock_user_with_2fa.email

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act
        result = await command.execute()

        # Assert
        assert result["requires_2fa"] is True
        assert "temporary_token" in result
        assert result["temporary_token"].startswith("token_")

        # Verify OTP was stored
        assert mock_user_with_2fa.id in otp_service.stored_otps
        assert otp_service.stored_otps[mock_user_with_2fa.id] == "123456"

        # Verify event was published
        assert len(event_publisher.published_events) == 1
        channel, event = event_publisher.published_events[0]
        assert channel == "email:otp"
        assert event["email"] == mock_user_with_2fa.email
        assert event["username"] == mock_user_with_2fa.username
        assert event["otp_code"] == "123456"

    async def test_authenticate_user_fails_with_invalid_email(
        self, mock_session, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = None

        password_service = MockPasswordService(should_verify=True)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await command.execute()

        assert "Email ou senha incorretos" in str(exc_info.value)

    async def test_authenticate_user_fails_with_invalid_password(
        self, mock_session, mock_user_without_2fa, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = mock_user_without_2fa

        password_service = MockPasswordService(should_verify=False)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            await command.execute()

        assert "Email ou senha incorretos" in str(exc_info.value)

    async def test_normal_login_creates_correct_token(
        self, mock_session, mock_user_without_2fa, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = mock_user_without_2fa

        password_service = MockPasswordService(should_verify=True)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act
        result = await command.execute()

        # Assert
        assert result["token"] == f"token_{mock_user_without_2fa.id}_60"

    async def test_2fa_login_creates_temporary_token(
        self, mock_session, mock_user_with_2fa, login_payload
    ):
        # Arrange
        mock_session._mock_scalars.first.return_value = mock_user_with_2fa

        password_service = MockPasswordService(should_verify=True)
        token_service = MockTokenService()
        otp_service = MockOtpService()
        event_publisher = MockEventPublisher()

        login_payload.email = mock_user_with_2fa.email

        command = LoginCommand(
            session=mock_session,
            password_service=password_service,
            token_service=token_service,
            otp_service=otp_service,
            event_publisher=event_publisher,
            payload=login_payload,
        )

        # Act
        result = await command.execute()

        # Assert
        assert result["temporary_token"] == f"token_{mock_user_with_2fa.id}_5"
        assert result["requires_2fa"] is True
