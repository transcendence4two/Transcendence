import pytest
import asyncio
from unittest.mock import MagicMock
from src.infrastructure.storage import StorageService
from src.core.settings import settings

@pytest.mark.asyncio
class TestStorageServiceValidation:
    async def test_upload_avatar_valid_file(self, monkeypatch):
        # Mock MinIO client internal call
        service = StorageService()
        service.client.put_object = MagicMock()
        
        file_content = b"fake data"
        filename = "test.png"
        
        url = await service.upload_avatar(file_content, filename)
        
        assert "avatars" in url
        assert url.endswith(".png")
        assert service.client.put_object.called

    async def test_upload_avatar_invalid_extension(self):
        service = StorageService()
        
        with pytest.raises(ValueError, match="Extension .txt not allowed"):
            await service.upload_avatar(b"data", "malicious.txt")

    async def test_upload_avatar_handles_missing_extension(self, monkeypatch):
        service = StorageService()
        service.client.put_object = MagicMock()
        
        # Should default to .jpg
        url = await service.upload_avatar(b"data", "filename_without_ext")
        assert url.endswith(".jpg")
