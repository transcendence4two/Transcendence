import pytest
from httpx import AsyncClient

from src.core.settings import settings
from src.domain.models.user import User
from src.domain.services.token import TokenService


@pytest.mark.asyncio
class TestUploadAvatarIntegration:
    """Integration tests for /users/me/avatar endpoint"""

    async def test_upload_avatar_success(
        self, client: AsyncClient, db_session, mock_storage_service
    ):
        # 1. Setup Db User
        user = User(
            id="integration-user-123",
            username="testavatar",
            email="avatar@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        # 2. Setup Token
        token = TokenService(settings.jwt_config).create_token("integration-user-123")
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create dummy file upload payload
        files = {
            "file": ("profile.png", b"fake_png_bytes", "image/png"),
        }

        # 4. Request
        response = await client.post("/users/me/avatar", headers=headers, files=files)

        # 5. Assertions
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == "integration-user-123"
        assert data["username"] == "testavatar"
        assert "avatar_url" in data
        assert data["avatar_url"] == "http://mock-minio/avatars/profile.png"

        # Verify the dependency override caught the internal file
        stored_file = mock_storage_service.uploaded_files.get("profile.png")
        assert stored_file is not None
        assert stored_file["content"] == b"fake_png_bytes"

    async def test_upload_avatar_without_file_fails(
        self, client: AsyncClient, db_session
    ):
        user = User(
            id="integration-user-no-file",
            username="nofileuser",
            email="nofile@example.com",
            hashed_password="hash",
            enable_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()

        token = TokenService(settings.jwt_config).create_token(
            "integration-user-no-file"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Request missing the 'files' kwarg
        response = await client.post("/users/me/avatar", headers=headers)

        assert response.status_code == 422
        assert "detail" in response.json()

    async def test_upload_avatar_unauthorized(self, client: AsyncClient):
        files = {
            "file": ("profile.png", b"fake_png_bytes", "image/png"),
        }
        # No Authorization header
        response = await client.post("/users/me/avatar", files=files)
        assert response.status_code == 401
