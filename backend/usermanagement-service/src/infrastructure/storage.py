import asyncio
import io
import uuid
from pathlib import Path

import structlog
from minio import Minio

from src.core.settings import settings

logger = structlog.get_logger()


class StorageService:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.public_url = settings.MINIO_PUBLIC_URL

    async def upload_avatar(self, file_content: bytes, original_filename: str) -> str:
        """Save avatar in MinIO and returns public URL"""
        extension = Path(original_filename).suffix.lower()
        if not extension:
            extension = ".jpg"

        if extension not in self.ALLOWED_EXTENSIONS:
            logger.warning("Attempted to upload invalid file type", extension=extension)
            supported = ", ".join(self.ALLOWED_EXTENSIONS)
            raise ValueError(
                f"Extension {extension} not allowed. Supported: {supported}"
            )

        file_name = f"{uuid.uuid4().hex}{extension}"

        try:
            data = io.BytesIO(file_content)
            length = len(file_content)

            content_type = f"image/{extension.lstrip('.')}"
            if extension in (".jpg", ".jpeg"):
                content_type = "image/jpeg"

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=file_name,
                    data=data,
                    length=length,
                    content_type=content_type,
                ),
            )

            logger.info("Avatar uploaded to MinIO successfully", file_name=file_name)

            return f"{self.public_url}/{self.bucket_name}/{file_name}"

        except Exception as e:
            logger.error("Failed to upload avatar to MinIO", error=str(e))
            raise e


storage_service = StorageService()
