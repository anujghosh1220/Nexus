import hashlib
import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.repositories.file_repository import FileRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.file import FileCreate, FileResponse, FileListResponse
from app.models.file import File
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.core.exceptions import AuthorizationError, ResourceNotFoundError, ValidationError
from app.core.config import settings
from app.utils.storage import get_storage_service, StorageService


class FileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_repo = FileRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()
        self.storage: StorageService = get_storage_service()

    async def upload_file(
        self,
        organization_id: str,
        requesting_user_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
    ) -> FileResponse:
        """Upload a file."""
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(file_data) > max_size:
            raise ValidationError(f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB")

        allowed_types = set(settings.allowed_file_types_list)
        if content_type not in allowed_types:
            raise ValidationError(f"File type {content_type} is not allowed")

        # Verify organization exists and user is a member
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        # Generate storage key and compute checksum
        storage_key = File.generate_storage_key(filename)
        checksum = hashlib.sha256(file_data).hexdigest()

        # Upload to storage
        await self.storage.upload(storage_key, file_data, content_type)

        # Create file record
        file = await self.file_repo.create(
            organization_id=organization_id,
            uploaded_by=requesting_user_id,
            filename=filename,
            storage_key=storage_key,
            content_type=content_type,
            size=len(file_data),
            checksum=checksum,
        )

        return FileResponse.model_validate(file)

    async def list_files(
        self,
        organization_id: str,
        requesting_user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> FileListResponse:
        """List files for an organization."""
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        files = await self.file_repo.list_by_organization(organization_id, limit, offset)
        total = await self.file_repo.count_by_organization(organization_id)

        return FileListResponse(
            items=[FileResponse.model_validate(f) for f in files],
            total=total,
        )

    async def get_file(
        self,
        file_id: str,
        requesting_user_id: str,
    ) -> FileResponse:
        """Get file metadata by ID."""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise ResourceNotFoundError("File")

        membership = await self.org_repo.get_membership(file.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        return FileResponse.model_validate(file)

    async def download_file(self, file_id: str, requesting_user_id: str) -> tuple[bytes, str, str]:
        """Download file data."""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise ResourceNotFoundError("File")

        if file.deleted_at is not None:
            raise ResourceNotFoundError("File")

        membership = await self.org_repo.get_membership(file.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        data = await self.storage.download(file.storage_key)
        return data, file.content_type, file.filename

    async def delete_file(self, file_id: str, requesting_user_id: str) -> None:
        """Delete a file."""
        file = await self.file_repo.get_by_id(file_id)
        if not file:
            raise ResourceNotFoundError("File")

        if file.deleted_at is not None:
            return

        membership = await self.org_repo.get_membership(file.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        await self.storage.delete(file.storage_key)
        await self.file_repo.soft_delete(file)
