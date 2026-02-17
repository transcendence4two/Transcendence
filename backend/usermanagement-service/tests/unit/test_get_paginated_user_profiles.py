import pytest

from src.domain.models.user import User
from src.domain.services.commands.get_paginated_users import (
    GetPaginatedUserProfilesCommand,
)
from src.domain.services.user import UserService


@pytest.mark.asyncio
class TestGetPaginatedUserProfilesCommand:
    """Unit tests for GetPaginatedUserProfilesCommand"""

    async def test_execute_returns_paginated_users_with_defaults(self, mock_session):
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
        session = mock_session(users_to_return=users, total_count=2)

        command = GetPaginatedUserProfilesCommand(session)
        result = await command.execute()

        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["total_pages"] == 1

    async def test_execute_returns_paginated_users_with_custom_page_size(
        self, mock_session
    ):
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
        session = mock_session(users_to_return=users, total_count=25)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=5)
        result = await command.execute()

        assert len(result["items"]) == 5
        assert result["total"] == 25
        assert result["page"] == 1
        assert result["page_size"] == 5
        assert result["total_pages"] == 5

    async def test_execute_returns_second_page_correctly(self, mock_session):
        users = [
            User(
                id="user-3",
                username="user3",
                email="user3@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = mock_session(users_to_return=users, total_count=15)

        command = GetPaginatedUserProfilesCommand(session, page=2, page_size=10)
        result = await command.execute()

        assert len(result["items"]) == 1
        assert result["total"] == 15
        assert result["page"] == 2
        assert result["page_size"] == 10
        assert result["total_pages"] == 2

    async def test_execute_returns_empty_list_when_no_users(self, mock_session):
        session = mock_session(users_to_return=[], total_count=0)

        command = GetPaginatedUserProfilesCommand(session)
        result = await command.execute()

        assert result["items"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["total_pages"] == 0

    async def test_execute_enforces_minimum_page_number(self, mock_session):
        users = [
            User(
                id="user-1",
                username="user1",
                email="user1@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = mock_session(users_to_return=users, total_count=1)

        command = GetPaginatedUserProfilesCommand(session, page=0, page_size=10)
        result = await command.execute()

        assert result["page"] == 1

    async def test_execute_enforces_minimum_page_size(self, mock_session):
        users = []
        session = mock_session(users_to_return=users, total_count=0)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=0)
        result = await command.execute()

        assert result["page_size"] == 1

    async def test_execute_enforces_maximum_page_size(self, mock_session):
        users = []
        session = mock_session(users_to_return=users, total_count=0)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=200)
        result = await command.execute()

        assert result["page_size"] == 100

    async def test_execute_calculates_total_pages_correctly(self, mock_session):
        users = []
        session = mock_session(users_to_return=users, total_count=45)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=10)
        result = await command.execute()

        assert result["total_pages"] == 5

    async def test_execute_calculates_total_pages_with_exact_division(
        self, mock_session
    ):
        users = []
        session = mock_session(users_to_return=users, total_count=50)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=10)
        result = await command.execute()

        assert result["total_pages"] == 5

    async def test_execute_handles_negative_page_number(self, mock_session):
        users = []
        session = mock_session(users_to_return=users, total_count=10)

        command = GetPaginatedUserProfilesCommand(session, page=-5, page_size=10)
        result = await command.execute()

        assert result["page"] == 1

    async def test_execute_handles_negative_page_size(self, mock_session):
        users = []
        session = mock_session(users_to_return=users, total_count=10)

        command = GetPaginatedUserProfilesCommand(session, page=1, page_size=-10)
        result = await command.execute()

        assert result["page_size"] == 1


@pytest.mark.asyncio
class TestUserServiceGetPaginatedUserProfiles:
    """Unit tests for UserService.get_paginated_user_profiles method"""

    async def test_get_paginated_user_profiles_returns_paginated_result(
        self, mock_session, mock_password_service, mock_event_publisher
    ):
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
        session = mock_session(users_to_return=users, total_count=2)

        service = UserService(session, mock_password_service, mock_event_publisher)
        result = await service.get_paginated_user_profiles(page=1, page_size=10)

        assert len(result["items"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1

    async def test_get_paginated_user_profiles_with_custom_parameters(
        self, mock_session, mock_password_service, mock_event_publisher
    ):
        users = []
        session = mock_session(users_to_return=users, total_count=50)

        service = UserService(session, mock_password_service, mock_event_publisher)
        result = await service.get_paginated_user_profiles(page=3, page_size=20)

        assert result["page"] == 3
        assert result["page_size"] == 20
        assert result["total"] == 50

    async def test_get_paginated_user_profiles_returns_empty_list(
        self, mock_session, mock_password_service, mock_event_publisher
    ):
        session = mock_session(users_to_return=[], total_count=0)

        service = UserService(session, mock_password_service, mock_event_publisher)
        result = await service.get_paginated_user_profiles()

        assert result["items"] == []
        assert result["total"] == 0
        assert result["total_pages"] == 0

    async def test_get_paginated_user_profiles_uses_default_values(
        self, mock_session, mock_password_service, mock_event_publisher
    ):
        users = [
            User(
                id="default-test",
                username="defaultuser",
                email="default@example.com",
                hashed_password="hash",
                enable_2fa=False,
            )
        ]
        session = mock_session(users_to_return=users, total_count=1)

        service = UserService(session, mock_password_service, mock_event_publisher)
        result = await service.get_paginated_user_profiles()

        assert result["page"] == 1
        assert result["page_size"] == 10
