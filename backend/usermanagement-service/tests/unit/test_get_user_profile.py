import pytest

from src.domain.exceptions import UserNotFoundError
from src.domain.models.user import User
from src.domain.services.commands.get_user_profile import GetUserProfileCommand
from src.domain.services.user import UserService


class MockSession:
    """Mock AsyncSession for testing"""

    def __init__(self, user_to_return=None):
        self.user_to_return = user_to_return
        self.executed_stmt = None

    async def execute(self, stmt):
        self.executed_stmt = stmt
        return MockResult(self.user_to_return)


class MockResult:
    """Mock result from database query"""

    def __init__(self, user):
        self.user = user

    def scalars(self):
        return self

    def first(self):
        return self.user


class MockPasswordService:
    """Mock password service"""

    def hash_password(self, password: str) -> str:
        return f"hashed_{password}"


class MockEventPublisher:
    """Mock event publisher"""

    def __init__(self):
        self.published_events = []

    async def publish(self, channel: str, data: dict):
        self.published_events.append({"channel": channel, "data": data})


@pytest.mark.asyncio
class TestGetUserProfileCommand:
    """Unit tests for GetUserProfileCommand"""

    async def test_execute_returns_user_when_found(self):
        user = User(
            id="test-id-123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pass",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)

        command = GetUserProfileCommand(session, "test-id-123")
        result = await command.execute()

        assert result == user
        assert result.id == "test-id-123"
        assert result.username == "testuser"
        assert result.email == "test@example.com"

    async def test_execute_raises_user_not_found_when_user_does_not_exist(self):
        session = MockSession(user_to_return=None)

        command = GetUserProfileCommand(session, "non-existent-id")

        with pytest.raises(UserNotFoundError) as exc_info:
            await command.execute()

        assert "User with id 'non-existent-id' not found" in str(exc_info.value)

    async def test_execute_queries_database_with_correct_user_id(self):
        user = User(
            id="user-123",
            username="john",
            email="john@example.com",
            hashed_password="hash",
            enable_2fa=True,
        )
        session = MockSession(user_to_return=user)

        command = GetUserProfileCommand(session, "user-123")
        await command.execute()

        assert session.executed_stmt is not None


@pytest.mark.asyncio
class TestUserServiceGetProfile:
    """Unit tests for UserService.get_user_profile method"""

    async def test_get_user_profile_returns_user(self):
        user = User(
            id="service-id-456",
            username="serviceuser",
            email="service@example.com",
            hashed_password="hashed",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_user_profile("service-id-456")

        assert result == user
        assert result.username == "serviceuser"

    async def test_get_user_profile_raises_when_user_not_found(self):
        session = MockSession(user_to_return=None)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)

        with pytest.raises(UserNotFoundError):
            await service.get_user_profile("missing-user")

    async def test_get_user_profile_with_2fa_enabled(self):
        user = User(
            id="2fa-user",
            username="secure_user",
            email="secure@example.com",
            hashed_password="very_secure",
            enable_2fa=True,
        )
        session = MockSession(user_to_return=user)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_user_profile("2fa-user")

        assert result.enable_2fa is True
        assert result.id == "2fa-user"
