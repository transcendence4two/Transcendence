import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User


@pytest.mark.asyncio
class TestUserRegistration:
    """Integration tests for /users/register endpoint"""

    async def test_register_user_success(
        self, client: AsyncClient, db_session: AsyncSession, mock_event_publisher
    ):
        # Arrange
        payload = {
            "username": "registertestuser",
            "email": "register-test@example.com",
            "password": "securepassword123",
            "enable_2fa": False,
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 201

        data = response.json()
        assert data["username"] == payload["username"]
        assert data["email"] == payload["email"]
        assert data["enable_2fa"] == payload["enable_2fa"]
        assert "id" in data
        assert "password" not in data

        result = await db_session.execute(
            select(User).where(User.username == payload["username"])
        )
        user = result.scalar_one_or_none()

        assert user is not None
        assert user.username == payload["username"]
        assert user.email == payload["email"]
        assert user.hashed_password != payload["password"]
        assert user.hashed_password.startswith("$2b$")

        # Verify welcome email event was published
        assert len(mock_event_publisher.published_events) == 1
        channel, event = mock_event_publisher.published_events[0]
        assert channel == "email:welcome"
        assert event["email"] == payload["email"]
        assert event["username"] == payload["username"]

    async def test_register_user_with_2fa_enabled(
        self, client: AsyncClient, mock_event_publisher
    ):
        # Arrange
        payload = {
            "username": "user_2fa",
            "email": "register-2fa@example.com",
            "password": "securepassword123",
            "enable_2fa": True,
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["enable_2fa"] is True

        # Verify welcome email event was published
        assert len(mock_event_publisher.published_events) == 1
        channel, event = mock_event_publisher.published_events[0]
        assert channel == "email:welcome"
        assert event["email"] == payload["email"]

    async def test_register_user_duplicate_username(self, client: AsyncClient):
        # Arrange
        payload = {
            "username": "duplicateuser",
            "email": "unique1@example.com",
            "password": "password123",
            "enable_2fa": False,
        }

        # Act - First registration (should succeed)
        response1 = await client.post("/users/register", json=payload)
        assert response1.status_code == 201

        # Act - Second registration with same username but different email
        payload2 = {
            "username": "duplicateuser",
            "email": "unique2@example.com",
            "password": "password456",
            "enable_2fa": False,
        }
        response2 = await client.post("/users/register", json=payload2)

        # Assert
        assert response2.status_code == 409
        data = response2.json()
        assert "error_type" in data
        assert data["error_type"] == "USER_ALREADY_EXISTS"
        assert "detail" in data

    async def test_register_user_duplicate_email(self, client: AsyncClient):
        # Arrange
        payload = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "password123",
            "enable_2fa": False,
        }

        # Act - First registration (should succeed)
        response1 = await client.post("/users/register", json=payload)
        assert response1.status_code == 201

        # Act - Second registration with different username but same email
        payload2 = {
            "username": "user2",  # Different username
            "email": "duplicate@example.com",  # Same email
            "password": "password456",
            "enable_2fa": False,
        }
        response2 = await client.post("/users/register", json=payload2)

        # Assert
        assert response2.status_code == 409
        data = response2.json()
        assert "error_type" in data
        assert data["error_type"] == "USER_ALREADY_EXISTS"

    async def test_register_user_invalid_email(self, client: AsyncClient):
        # Arrange
        payload = {
            "username": "testuser",
            "email": "invalid-email-format",
            "password": "password123",
            "enable_2fa": False,
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_user_short_password(self, client: AsyncClient):
        # Arrange
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",  # short password
            "enable_2fa": False,
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_user_empty_username(self, client: AsyncClient):
        # Arrange
        payload = {
            "username": "",  # Empty username
            "email": "test@example.com",
            "password": "password123",
            "enable_2fa": False,
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_user_missing_required_fields(self, client: AsyncClient):
        # Arrange
        payload = {"username": "testuser"}

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_user_default_2fa_false(self, client: AsyncClient):
        # Arrange - No enable_2fa field
        payload = {
            "username": "default2fa",
            "email": "default@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["enable_2fa"] is False
