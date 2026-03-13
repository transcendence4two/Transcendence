import pytest

from src.domain.exceptions import UserNotFoundError
from src.domain.models.user import User
from src.domain.services.user import UserService


@pytest.mark.asyncio
class TestUserServiceUploadAvatar:
    """Unit tests for UserService.upload_avatar method"""

    async def test_upload_avatar_returns_updated_user_with_mock_url(
        self,
        mock_session,
        mock_password_service,
        mock_token_service,
        mock_otp_service,
        mock_event_publisher,
        mock_storage_service,
    ):
        user = User(
            id="avatar-id-123",
            username="test_avatar_user",
            email="avatar@example.com",
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
            mock_storage_service,
        )
        
        file_bytes = b"fake_image_content"
        filename = "myphoto.png"
        
        result = await service.upload_avatar("avatar-id-123", file_bytes, filename)

        assert result.id == "avatar-id-123"
        assert result.avatar_url == "http://mock-minio/avatars/myphoto.png"
        
        # Ensure the file was actually stored in the mock
        stored_file = mock_storage_service.uploaded_files["myphoto.png"]
        assert stored_file["content"] == b"fake_image_content"
        assert stored_file["url"] == "http://mock-minio/avatars/myphoto.png"
        assert session.committed is True

    async def test_upload_avatar_raises_when_user_not_found(
        self,
        mock_session,
        mock_password_service,
        mock_token_service,
        mock_otp_service,
        mock_event_publisher,
        mock_storage_service,
    ):
        session = mock_session(user_to_return=None)

        service = UserService(
            session,
            mock_password_service,
            mock_token_service,
            mock_otp_service,
            mock_event_publisher,
            mock_storage_service,
        )

        with pytest.raises(UserNotFoundError):
            await service.upload_avatar("missing-user", b"content", "file.png")
