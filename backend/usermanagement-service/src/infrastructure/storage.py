import io
import uuid

import structlog
from minio import Minio

from src.core.settings import settings

logger = structlog.get_logger()


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )
        self.bucket_name = "avatars"
        self.public_url = settings.MINIO_PUBLIC_URL

    def upload_avatar(self, file_content: bytes, original_filename: str) -> str:
        """Save avatar in MinIO and returns public URl"""
        extension = (
            original_filename.split(".")[-1] if "." in original_filename else "jpg"
        )
        file_name = f"{uuid.uuid4().hex}.{extension}"

        try:
            data = io.BytesIO(file_content)
            length = len(file_content)

            content_type = f"image/{extension.lower()}"
            if extension.lower() == "jpg":
                content_type = "image/jpeg"

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=data,
                length=length,
                content_type=content_type,
            )

            logger.info("Avatar uploaded to MinIO successfully", file_name=file_name)

            return f"{self.public_url}/{self.bucket_name}/{file_name}"

        except Exception as e:
            logger.error("Failed to upload avatar to MinIO", error=str(e))
            raise e


storage_service = StorageService()
