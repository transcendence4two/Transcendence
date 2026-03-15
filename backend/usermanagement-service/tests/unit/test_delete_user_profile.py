import pytest

from src.domain.exceptions import (
    InvalidDeleteConfirmationError,
    UserNotFoundError,
)
from src.domain.models.user import User
from src.domain.services.commands.delete_user_profile import DeleteUserProfileCommand
from src.domain.services.user import UserService


@pytest.mark.asyncio
class TestDeleteUserProfileCommand:
    """Unit tests for DeleteUserProfileCommand."""

    async def test_execute_deletes_user_when_confirmation_is_valid(self, mock_session):
        user = User(
            id="delete-user-1",
            username="delete-me",
            email="delete@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        command = DeleteUserProfileCommand(
            session,
            user_id="delete-user-1",
            confirmation_text="Yes, delete my user",
        )

        await command.execute()

        assert session.committed is True
        assert session.deleted_entities == [user]

    async def test_execute_raises_when_confirmation_is_invalid(self, mock_session):
        user = User(
            id="delete-user-2",
            username="keep-me",
            email="keep@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        command = DeleteUserProfileCommand(
            session,
            user_id="delete-user-2",
            confirmation_text="yes",
        )

        with pytest.raises(InvalidDeleteConfirmationError) as exc_info:
            await command.execute()

        assert "Invalid confirmation text" in str(exc_info.value)
        assert session.deleted_entities == []
        assert session.committed is False

    async def test_execute_raises_when_user_not_found(self, mock_session):
        session = mock_session(user_to_return=None)

        command = DeleteUserProfileCommand(
            session,
            user_id="missing-user",
            confirmation_text="Yes, delete my user",
        )

        with pytest.raises(UserNotFoundError) as exc_info:
            await command.execute()

        assert "User with id 'missing-user' not found" in str(exc_info.value)


@pytest.mark.asyncio
class TestUserServiceDeleteProfile:
    """Unit tests for UserService.delete_user_profile method."""

    async def test_delete_user_profile_calls_command_and_deletes(
        self,
        mock_session,
        mock_password_service,
        mock_token_service,
        mock_otp_service,
        mock_event_publisher,
    ):
        user = User(
            id="service-delete-user",
            username="service-delete",
            email="service-delete@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        session = mock_session(user_to_return=user)

        service = UserService(
            session,
            mock_password_service,
            mock_token_service,
            mock_otp_service,
            mock_event_publisher,
        )

        await service.delete_user_profile(
            user_id="service-delete-user",
            confirmation_text="Yes, delete my user",
        )

        assert session.committed is True
        assert len(session.deleted_entities) == 1
        assert session.deleted_entities[0].id == "service-delete-user"
