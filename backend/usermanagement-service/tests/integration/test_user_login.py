"""Integration tests for /users/login endpoint"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User
from src.domain.services.password import PasswordService


@pytest.mark.asyncio
class TestUserLogin:
    """Integration tests for /users/login endpoint"""

    async def test_login_success_without_2fa(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange - Register a user first
        password_service = PasswordService()
        user = User(
            id="test-user-id",
            username="loginuser",
            email="login@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "login@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "login@example.com"
        assert data["user"]["username"] == "loginuser"
        assert data["user"]["enable_2fa"] is False
        assert "password" not in data["user"]

    async def test_login_success_with_2fa_enabled(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        mock_event_publisher,
        mock_otp_service,
    ):
        # Arrange - Register a user with 2FA enabled
        password_service = PasswordService()
        user = User(
            id="test-user-2fa-id",
            username="user2fa",
            email="2fa@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=True,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "2fa@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 202

        data = response.json()
        assert "temporary_token" in data
        assert data["2fa_required"] is True
        assert data["message"] == "Código de verificação enviado para seu email"
        assert "access_token" not in data

        # Verify OTP was generated and stored
        assert "test-user-2fa-id" in mock_otp_service.stored_otps

        # Verify event was published
        assert len(mock_event_publisher.published_events) == 1
        channel, event = mock_event_publisher.published_events[0]
        assert channel == "email:otp"

    async def test_login_fails_with_invalid_email(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange
        login_payload = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 401

        data = response.json()
        assert "error_type" in data
        assert data["error_type"] == "INVALID_CREDENTIALS"
        assert "detail" in data
        assert "Email ou senha incorretos" in data["detail"]

    async def test_login_fails_with_invalid_password(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange - Register a user first
        password_service = PasswordService()
        user = User(
            id="test-user-wrong-pwd",
            username="testuser",
            email="test@example.com",
            hashed_password=password_service.hash_password("correctpassword"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 401

        data = response.json()
        assert "error_type" in data
        assert data["error_type"] == "INVALID_CREDENTIALS"
        assert "Email ou senha incorretos" in data["detail"]

    async def test_login_fails_with_missing_email(self, client: AsyncClient):
        # Arrange
        login_payload = {
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_fails_with_missing_password(self, client: AsyncClient):
        # Arrange
        login_payload = {
            "email": "test@example.com",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_fails_with_invalid_email_format(self, client: AsyncClient):
        # Arrange
        login_payload = {
            "email": "not-an-email",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_with_2fa_generates_otp_and_publishes_event(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        mock_event_publisher,
        mock_otp_service,
    ):
        # Arrange - Register a user with 2FA enabled
        password_service = PasswordService()
        user = User(
            id="test-user-otp",
            username="otpuser",
            email="otp@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=True,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "otp@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 202
        data = response.json()
        assert "temporary_token" in data

        # Verify OTP was stored
        assert "test-user-otp" in mock_otp_service.stored_otps
        stored_otp = mock_otp_service.stored_otps["test-user-otp"]
        assert stored_otp == "123456"  # MockOtpService always generates this OTP

        # Verify event was published
        assert len(mock_event_publisher.published_events) == 1
        channel, event = mock_event_publisher.published_events[0]
        assert channel == "email:otp"
        assert event["email"] == "otp@example.com"
        assert event["username"] == "otpuser"
        assert event["otp_code"] == "123456"

    async def test_otp_verification_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        mock_otp_service,
        mock_event_publisher,
    ):
        """Test that OTP can be verified after login with 2FA"""
        # Arrange - Register a user with 2FA enabled
        password_service = PasswordService()
        user = User(
            id="test-user-verify-otp",
            username="verifyuser",
            email="verify@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=True,
        )
        db_session.add(user)
        await db_session.commit()

        # Act - Login to generate OTP
        login_payload = {
            "email": "verify@example.com",
            "password": "password123",
        }
        response = await client.post("/users/login", json=login_payload)

        # Assert - Verify login response
        assert response.status_code == 202
        data = response.json()
        assert "temporary_token" in data

        # Verify OTP was stored and can be retrieved
        assert "test-user-verify-otp" in mock_otp_service.stored_otps
        stored_otp = mock_otp_service.stored_otps["test-user-verify-otp"]

        # Simulate OTP verification
        is_valid = await mock_otp_service.verify_otp("test-user-verify-otp", stored_otp)
        assert is_valid is True

        # OTP should be removed after verification
        assert "test-user-verify-otp" not in mock_otp_service.stored_otps

        # Verify wrong OTP fails
        mock_otp_service.stored_otps["test-user-verify-otp"] = "123456"
        is_valid = await mock_otp_service.verify_otp("test-user-verify-otp", "999999")
        assert is_valid is False

    async def test_login_multiple_times_with_same_credentials(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange
        password_service = PasswordService()
        user = User(
            id="test-user-multiple",
            username="multiplelogin",
            email="multiple@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "multiple@example.com",
            "password": "password123",
        }

        # Act - Login multiple times
        response1 = await client.post("/users/login", json=login_payload)
        response2 = await client.post("/users/login", json=login_payload)
        response3 = await client.post("/users/login", json=login_payload)

        # Assert - All logins should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Each response should return a valid token
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        token3 = response3.json()["access_token"]

        # All tokens should be valid and not empty
        assert token1
        assert token2
        assert token3

    async def test_login_case_sensitive_email(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange
        password_service = PasswordService()
        user = User(
            id="test-user-case",
            username="caseuser",
            email="Case@Example.COM",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        # Act - Try to login with different case
        login_payload = {
            "email": "case@example.com",
            "password": "password123",
        }
        response = await client.post("/users/login", json=login_payload)

        # Assert - Should fail because email is case-sensitive in the database
        assert response.status_code == 401

    async def test_login_returns_correct_user_data(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        # Arrange
        password_service = PasswordService()
        user = User(
            id="test-user-data",
            username="datauser",
            email="userdata@example.com",
            hashed_password=password_service.hash_password("password123"),
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        login_payload = {
            "email": "userdata@example.com",
            "password": "password123",
        }

        # Act
        response = await client.post("/users/login", json=login_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()

        user_data = data["user"]
        assert user_data["id"] == "test-user-data"
        assert user_data["username"] == "datauser"
        assert user_data["email"] == "userdata@example.com"
        assert user_data["enable_2fa"] is False
        assert "hashed_password" not in user_data
        assert "password" not in user_data
