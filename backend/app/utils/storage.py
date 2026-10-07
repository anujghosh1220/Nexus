import hashlib
import os
import aiofiles
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings


class StorageService(ABC):
    """Abstract storage service."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload data and return the storage key."""
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download data by storage key."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data by storage key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if data exists."""
        pass

    @abstractmethod
    def generate_access_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for access."""
        pass


class LocalStorageService(StorageService):
    """Local filesystem storage service for development."""

    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        file_path = os.path.join(self.base_path, key)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        return key

    async def download(self, key: str) -> bytes:
        file_path = os.path.join(self.base_path, key)
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> bool:
        file_path = os.path.join(self.base_path, key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    async def exists(self, key: str) -> bool:
        file_path = os.path.join(self.base_path, key)
        return os.path.exists(file_path)

    def generate_access_url(self, key: str, expires_in: int = 3600) -> str:
        return f"/api/v1/files/{key}/download"


class S3StorageService(StorageService):
    """S3-compatible object storage service."""

    def __init__(self):
        import boto3
        self.bucket = settings.STORAGE_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            use_ssl=settings.STORAGE_USE_SSL,
        )

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        )
        return key

    async def download(self, key: str) -> bytes:
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.get_object(Bucket=self.bucket, Key=key)
        )
        return response["Body"].read()

    async def delete(self, key: str) -> bool:
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_object(Bucket=self.bucket, Key=key)
            )
            return True
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.head_object(Bucket=self.bucket, Key=key)
            )
            return True
        except Exception:
            return False

    def generate_access_url(self, key: str, expires_in: int = 3600) -> str:
        import boto3
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url


def get_storage_service() -> StorageService:
    """Get the configured storage service."""
    storage_type = os.environ.get("STORAGE_TYPE", "local").lower()
    if storage_type == "s3":
        return S3StorageService()
    return LocalStorageService()
