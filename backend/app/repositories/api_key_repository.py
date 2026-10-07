from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.api_key import ApiKey
from datetime import datetime


class ApiKeyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: str,
        created_by: str,
        name: str,
        key_prefix: str,
        key_hash: str,
        scopes: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> ApiKey:
        """Create a new API key."""
        api_key = ApiKey(
            id=ApiKey._generate_id(),
            organization_id=organization_id,
            created_by=created_by,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=scopes,
            expires_at=expires_at,
        )
        self.db.add(api_key)
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key

    async def get_by_id(self, api_key_id: str) -> Optional[ApiKey]:
        """Get API key by ID."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == api_key_id)
        )
        return result.scalar_one_or_none()

    async def get_by_prefix(self, key_prefix: str) -> Optional[ApiKey]:
        """Get API key by prefix."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_prefix == key_prefix)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ApiKey]:
        """List API keys for an organization."""
        result = await self.db.execute(
            select(ApiKey)
            .where(ApiKey.organization_id == organization_id)
            .order_by(ApiKey.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def count_by_organization(self, organization_id: str) -> int:
        """Count API keys for an organization."""
        from sqlalchemy import func as sa_func
        result = await self.db.execute(
            select(sa_func.count(ApiKey.id)).where(ApiKey.organization_id == organization_id)
        )
        return result.scalar_one()

    async def revoke(self, api_key: ApiKey) -> ApiKey:
        """Revoke an API key."""
        api_key.revoked_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key

    async def update_last_used(self, api_key: ApiKey) -> ApiKey:
        """Update last used timestamp."""
        api_key.last_used_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key
