from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime
from app.models.file import File


class FileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: str,
        uploaded_by: str,
        filename: str,
        storage_key: str,
        content_type: str,
        size: int,
        checksum: str,
    ) -> File:
        """Create a new file record."""
        file = File(
            id=File._generate_id(),
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            filename=filename,
            storage_key=storage_key,
            content_type=content_type,
            size=size,
            checksum=checksum,
        )
        self.db.add(file)
        await self.db.flush()
        await self.db.refresh(file)
        return file

    async def get_by_id(self, file_id: str) -> Optional[File]:
        """Get file by ID."""
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()

    async def get_by_storage_key(self, storage_key: str) -> Optional[File]:
        """Get file by storage key."""
        result = await self.db.execute(
            select(File).where(File.storage_key == storage_key)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[File]:
        """List files for an organization."""
        result = await self.db.execute(
            select(File)
            .where(
                and_(
                    File.organization_id == organization_id,
                    File.deleted_at.is_(None)
                )
            )
            .order_by(File.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def count_by_organization(self, organization_id: str) -> int:
        """Count files for an organization."""
        from sqlalchemy import func as sa_func
        result = await self.db.execute(
            select(sa_func.count(File.id)).where(
                and_(
                    File.organization_id == organization_id,
                    File.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one()

    async def soft_delete(self, file: File) -> File:
        """Soft delete a file."""
        file.deleted_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(file)
        return file
