import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings
from src.domain.models.user import User
from src.domain.services.password import PasswordService
from src.domain.services.token import TokenService


@pytest.mark.asyncio
class TestUserDelete:
    """Integration tests for /users/{user_id} delete endpoint."""

    async def test_delete_user_success_with_valid_confirmation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        password_service = PasswordService()
        user = User(
            id="delete-int-1",
            username="deleteint",
            email="delete-int@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        token = TokenService(settings.jwt_config).create_token("delete-int-1")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.request(
            "DELETE",
            "/users/delete-int-1",
            headers=headers,
            json={"confirmation_text": "Yes, delete my user"},
        )

        assert response.status_code == 204

        result = await db_session.execute(select(User).where(User.id == "delete-int-1"))
        assert result.scalar_one_or_none() is None

    async def test_delete_user_fails_when_token_subject_is_different(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        password_service = PasswordService()
        user = User(
            id="delete-int-2",
            username="deleteint2",
            email="delete-int-2@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        token = TokenService(settings.jwt_config).create_token("another-user")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.request(
            "DELETE",
            "/users/delete-int-2",
            headers=headers,
            json={"confirmation_text": "Yes, delete my user"},
        )

        assert response.status_code == 403
        assert response.json()["error_type"] == "UNAUTHORIZED_ACTION"

        result = await db_session.execute(select(User).where(User.id == "delete-int-2"))
        assert result.scalar_one_or_none() is not None

    async def test_delete_user_fails_with_invalid_confirmation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        password_service = PasswordService()
        user = User(
            id="delete-int-3",
            username="deleteint3",
            email="delete-int-3@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        token = TokenService(settings.jwt_config).create_token("delete-int-3")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.request(
            "DELETE",
            "/users/delete-int-3",
            headers=headers,
            json={"confirmation_text": "delete"},
        )

        assert response.status_code == 400
        assert response.json()["error_type"] == "INVALID_DELETE_CONFIRMATION"

        result = await db_session.execute(select(User).where(User.id == "delete-int-3"))
        assert result.scalar_one_or_none() is not None
