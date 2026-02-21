import pytest

from src.domain.exceptions import UserNotFoundError
from src.domain.models.user import User
from src.domain.services.commands.toggle_2fa import Toggle2FACommand
from src.domain.services.user import UserService


@pytest.mark.asyncio
class TestToggle2FACommand:
    """Unit tests for Toggle2FACommand"""

    async def test_execute_enables_2fa_successfully(self, mock_session):
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        command = Toggle2FACommand(session, "user-123", enable=True)
        result = await command.execute()

        assert result.enable_2fa is True
        assert result.id == "user-123"
        assert session.committed is True

    async def test_execute_disables_2fa_successfully(self, mock_session):
        user = User(
            id="user-456",
            username="secureuser",
            email="secure@example.com",
            hashed_password="hash",
            enable_2fa=True,
        )
        session = mock_session(user_to_return=user)

        command = Toggle2FACommand(session, "user-456", enable=False)
        result = await command.execute()

        assert result.enable_2fa is False
        assert result.id == "user-456"
        assert session.committed is True

    async def test_execute_raises_when_user_not_found(self, mock_session):
        session = mock_session(user_to_return=None)

        command = Toggle2FACommand(session, "non-existent", enable=True)

        with pytest.raises(UserNotFoundError) as exc_info:
            await command.execute()

        assert "User with id 'non-existent' not found" in str(exc_info.value)

    async def test_execute_toggle_from_false_to_true(self, mock_session):
        user = User(
            id="toggle-user-1",
            username="toggleuser",
            email="toggle@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        command = Toggle2FACommand(session, "toggle-user-1", enable=True)
        result = await command.execute()

        assert result.enable_2fa is True

    async def test_execute_toggle_from_true_to_false(self, mock_session):
        user = User(
            id="toggle-user-2",
            username="anotheruser",
            email="another@example.com",
            hashed_password="hash",
            enable_2fa=True,
        )
        session = mock_session(user_to_return=user)

        command = Toggle2FACommand(session, "toggle-user-2", enable=False)
        result = await command.execute()

        assert result.enable_2fa is False

    async def test_execute_preserves_other_user_fields(self, mock_session):
        user = User(
            id="preserve-test",
            username="preserveuser",
            email="preserve@example.com",
            hashed_password="secret_hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        command = Toggle2FACommand(session, "preserve-test", enable=True)
        result = await command.execute()

        assert result.username == "preserveuser"
        assert result.email == "preserve@example.com"
        assert result.hashed_password == "secret_hash"
        assert result.enable_2fa is True


@pytest.mark.asyncio
class TestUserServiceToggle2FA:
    """Unit tests for UserService.toggle_2fa method"""

    async def test_toggle_2fa_enables_2fa(
        self, mock_session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher
    ):
        user = User(
            id="service-2fa-id",
            username="2fauser",
            email="2fa@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        service = UserService(session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher)
        result = await service.toggle_2fa("service-2fa-id", enable=True)

        assert result.enable_2fa is True
        assert result.id == "service-2fa-id"

    async def test_toggle_2fa_disables_2fa(
        self, mock_session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher
    ):
        user = User(
            id="disable-2fa-id",
            username="disableuser",
            email="disable@example.com",
            hashed_password="hash",
            enable_2fa=True,
        )
        session = mock_session(user_to_return=user)

        service = UserService(session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher)
        result = await service.toggle_2fa("disable-2fa-id", enable=False)

        assert result.enable_2fa is False

    async def test_toggle_2fa_raises_when_user_not_found(
        self, mock_session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher
    ):
        session = mock_session(user_to_return=None)

        service = UserService(session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher)

        with pytest.raises(UserNotFoundError):
            await service.toggle_2fa("missing-user", enable=True)

    async def test_toggle_2fa_returns_updated_user_object(
        self, mock_session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher
    ):
        user = User(
            id="return-test",
            username="returnuser",
            email="return@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        service = UserService(session, mock_password_service, mock_token_service, mock_otp_service, mock_event_publisher)
        result = await service.toggle_2fa("return-test", enable=True)

        assert isinstance(result, User)
        assert result.username == "returnuser"
        assert result.email == "return@example.com"
        assert result.enable_2fa is True
