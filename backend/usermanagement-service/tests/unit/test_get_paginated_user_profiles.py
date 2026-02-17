import pytest

from src.domain.models.user import User
from src.domain.services.commands.get_paginated_users import (
    GetPaginatedUserProfilesCommand,
)
from src.domain.services.user import UserService


class MockSession:
    """Mock AsyncSession for testing pagination"""

    def __init__(self, users_to_return=None, total_count=0):
        self.users_to_return = users_to_return or []
        self.total_count = total_count
        self.executed_stmts = []
        self.query_count = 0

    async def execute(self, stmt):
        self.executed_stmts.append(stmt)
        self.query_count += 1

        # First query is always count
        if self.query_count == 1:
            return MockCountResult(self.total_count)

        # Second query returns users
        return MockUsersResult(self.users_to_return)


class MockCountResult:
    """Mock result for count query"""

    def __init__(self, count):
        self.count = count

    def scalar(self):
        return self.count


class MockUsersResult:
    """Mock result for users query"""

    def __init__(self, users):
        self.users = users

    def scalars(self):
        return self

    def all(self):
        return self.users


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
class TestGetPaginatedUserProfilesCommand:
    """Unit tests for GetPaginatedUserProfilesCommand"""

    async def test_execute_returns_paginated_users_with_defaults(self):
        users = [
            User(
                id="user-1",
                username="user1",
                email="user1@example.com",
                hashed_password="hash",
                enable_2fa=False,
            ),
            User(
                id="user-2",
                username="user2",
                email="user2@example.com",
                hashed_password="hash",
                enable_2fa=False,
            ),
        ]
        session = MockSession(users_to_return=users, total_count=2)

        command = GetPaginatedUserProfilesCommand(session)
        result = await command.execute()

        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["total_pages"] == 1

    async def test_execute_returns_paginated_users_with_custom_page_size(self):
        users = [
            User(
                id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
            for i in range(5)
        ]
        session = MockSession(users_to_return=users, total_count=25)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=5)
        result = await command.execute()

        assert len(result["items"]) == 5
        assert result["total"] == 25
        assert result["page"] == 1
        assert result["page_size"] == 5
        assert result["total_pages"] == 5

    async def test_execute_returns_second_page_correctly(self):
        users = [
            User(
                id="user-3",
                username="user3",
                email="user3@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = MockSession(users_to_return=users, total_count=15)

        command = GetPaginatedUserProfilesCommand(session, page=2, page_size=10)
        result = await command.execute()

        assert len(result["items"]) == 1
        assert result["total"] == 15
        assert result["page"] == 2
        assert result["page_size"] == 10
        assert result["total_pages"] == 2

    async def test_execute_returns_empty_list_when_no_users(self):
        session = MockSession(users_to_return=[], total_count=0)

        command = GetPaginatedUserProfilesCommand(session)
        result = await command.execute()

        assert result["items"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["total_pages"] == 0

    async def test_execute_enforces_minimum_page_number(self):
        users = [
            User(
                id="user-1",
                username="user1",
                email="user1@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = MockSession(users_to_return=users, total_count=1)

        command = GetPaginatedUserProfilesCommand(session, page=0, page_size=10)
        result = await command.execute()

        assert result["page"] == 1

    async def test_execute_enforces_minimum_page_size(self):
        users = []
        session = MockSession(users_to_return=users, total_count=0)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=0)
        result = await command.execute()

        assert result["page_size"] == 1

    async def test_execute_enforces_maximum_page_size(self):
        users = []
        session = MockSession(users_to_return=users, total_count=0)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=200)
        result = await command.execute()

        assert result["page_size"] == 100

    async def test_execute_calculates_total_pages_correctly(self):
        users = []
        session = MockSession(users_to_return=users, total_count=45)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=10)
        result = await command.execute()

        assert result["total_pages"] == 5

    async def test_execute_calculates_total_pages_with_exact_division(self):
        users = []
        session = MockSession(users_to_return=users, total_count=50)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=10)
        result = await command.execute()

        assert result["total_pages"] == 5

    async def test_execute_handles_negative_page_number(self):
        users = []
        session = MockSession(users_to_return=users, total_count=10)

        command = GetPaginatedUserProfilesCommand(session, page=-5, page_size=10)
        result = await command.execute()

        assert result["page"] == 1

    async def test_execute_handles_negative_page_size(self):
        users = []
        session = MockSession(users_to_return=users, total_count=10)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=-10)
        result = await command.execute()

        assert result["page_size"] == 1


@pytest.mark.asyncio
class TestUserServiceGetPaginatedUserProfiles:
    """Unit tests for UserService.get_paginated_user_profiles method"""

    async def test_get_paginated_user_profiles_returns_paginated_result(self):
        users = [
            User(
                id="service-1",
                username="serviceuser1",
                email="service1@example.com",
                hashed_password="hash",
                enable_2fa=False,
            ),
            User(
                id="service-2",
                username="serviceuser2",
                email="service2@example.com",
                hashed_password="hash",
                enable_2fa=True,
            ),
        ]
        session = MockSession(users_to_return=users, total_count=2)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_paginated_user_profiles(page=1, page_size=10)

        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1

    async def test_get_paginated_user_profiles_with_custom_parameters(self):
        users = []
        session = MockSession(users_to_return=users, total_count=50)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_paginated_user_profiles(page=3, page_size=20)

        assert result["page"] == 3
        assert result["page_size"] == 20
        assert result["total"] == 50

    async def test_get_paginated_user_profiles_returns_empty_list(self):
        session = MockSession(users_to_return=[], total_count=0)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_paginated_user_profiles()

        assert result["items"] == []
        assert result["total"] == 0
        assert result["total_pages"] == 0

    async def test_get_paginated_user_profiles_uses_default_values(self):
        users = [
            User(
                id="default-test",
                username="defaultuser",
                email="default@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = MockSession(users_to_return=users, total_count=1)
        password_service = MockPasswordService()
        event_publisher = MockEventPublisher()

        service = UserService(session, password_service, event_publisher)
        result = await service.get_paginated_user_profiles()

        assert result["page"] == 1
        assert result["page_size"] == 10
