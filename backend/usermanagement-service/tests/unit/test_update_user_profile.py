import pytest

from src.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.models.user import User
from src.domain.schemas.user import UserProfileUpdateRequest
from src.domain.services.commands.update_user_profile import UpdateUserProfileCommand
from src.domain.services.user import UserService


class MockSession:
    """Mock AsyncSession for testing"""

    def __init__(self, user_to_return=None, conflicting_user=None):
        self.user_to_return = user_to_return
        self.conflicting_user = conflicting_user
        self.executed_stmts = []
        self.added_entities = []
        self.committed = False
        self.query_count = 0

    async def execute(self, stmt):
        self.executed_stmts.append(stmt)
        self.query_count += 1

        if self.query_count == 1:
            return MockResult(self.user_to_return)

        return MockResult(self.conflicting_user)

    def add(self, entity):
        self.added_entities.append(entity)

    async def commit(self):
        self.committed = True

    async def refresh(self, entity):
        pass


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
class TestUpdateUserProfileCommand:
    """Unit tests for UpdateUserProfileCommand"""

    async def test_execute_updates_username_successfully(self):
        user = User(
            id="user-123",
            username="oldusername",
            email="old@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        payload = UserProfileUpdateRequest(username="newusername")

        command = UpdateUserProfileCommand(session, "user-123", payload)
        result = await command.execute()

        assert result.username == "newusername"
        assert result.email == "old@example.com"
        assert session.committed is True

    async def test_execute_updates_email_successfully(self):
        user = User(
            id="user-456",
            username="testuser",
            email="old@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        payload = UserProfileUpdateRequest(email="new@example.com")

        command = UpdateUserProfileCommand(session, "user-456", payload)
        result = await command.execute()

        assert result.username == "testuser"
        assert result.email == "new@example.com"
        assert session.committed is True

    async def test_execute_updates_both_username_and_email(self):
        user = User(
            id="user-789",
            username="oldname",
            email="old@example.com",
            hashed_password="hash",
            enable_2fa=True,
        )
        session = MockSession(user_to_return=user)
        payload = UserProfileUpdateRequest(username="newname", email="new@example.com")

        command = UpdateUserProfileCommand(session, "user-789", payload)
        result = await command.execute()

        assert result.username == "newname"
        assert result.email == "new@example.com"
        assert result.enable_2fa is True

    async def test_execute_raises_when_user_not_found(self):
        session = MockSession(user_to_return=None)
        payload = UserProfileUpdateRequest(username="newusername")

        command = UpdateUserProfileCommand(session, "non-existent", payload)

        with pytest.raises(UserNotFoundError) as exc_info:
            await command.execute()

        assert "User with id 'non-existent' not found" in str(exc_info.value)

    async def test_execute_raises_when_username_already_taken(self):
        user = User(
            id="user-123",
            username="currentuser",
            email="current@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        conflicting_user = User(
            id="user-999",
            username="takenusername",
            email="other@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user, conflicting_user=conflicting_user)
        payload = UserProfileUpdateRequest(username="takenusername")

        command = UpdateUserProfileCommand(session, "user-123", payload)

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await command.execute()

        assert "Username 'takenusername' is already taken" in str(exc_info.value)

    async def test_execute_raises_when_email_already_registered(self):
        user = User(
            id="user-123",
            username="testuser",
            email="current@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        conflicting_user = User(
            id="user-888",
            username="otheruser",
            email="taken@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user, conflicting_user=conflicting_user)
        payload = UserProfileUpdateRequest(email="taken@example.com")

        command = UpdateUserProfileCommand(session, "user-123", payload)

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await command.execute()

        assert "Email 'taken@example.com' is already registered" in str(exc_info.value)

    async def test_execute_with_no_changes_provided(self):
        user = User(
            id="user-000",
            username="unchanged",
            email="unchanged@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        payload = UserProfileUpdateRequest()

        command = UpdateUserProfileCommand(session, "user-000", payload)
        result = await command.execute()

        assert result.username == "unchanged"
        assert result.email == "unchanged@example.com"


@pytest.mark.asyncio
class TestUserServiceUpdateProfile:
    """Unit tests for UserService.update_user_profile method"""

    async def test_update_user_profile_returns_updated_user(self):
        user = User(
            id="service-id-123",
            username="oldname",
            email="old@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        payload = UserProfileUpdateRequest(username="newname")
        result = await service.update_user_profile("service-id-123", payload)

        assert result.username == "newname"
        assert result.id == "service-id-123"

    async def test_update_user_profile_raises_when_user_not_found(self):
        session = MockSession(user_to_return=None)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        payload = UserProfileUpdateRequest(username="newname")

        with pytest.raises(UserNotFoundError):
            await service.update_user_profile("missing-user", payload)

    async def test_update_user_profile_updates_email(self):
        user = User(
            id="email-update-id",
            username="testuser",
            email="old@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = MockSession(user_to_return=user)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        payload = UserProfileUpdateRequest(email="new@example.com")
        result = await service.update_user_profile("email-update-id", payload)

        assert result.email == "new@example.com"
        assert result.username == "testuser"
