from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        changes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create a new audit log entry."""
        audit_log = AuditLog(
            id=AuditLog._generate_id(),
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(audit_log)
        await self.db.flush()
        await self.db.refresh(audit_log)
        return audit_log

    async def list_by_organization(
        self,
        organization_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AuditLog]:
        """List audit logs for an organization with optional filters."""
        query = select(AuditLog).where(AuditLog.organization_id == organization_id)

        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_by_organization(
        self,
        organization_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """Count audit logs for an organization with optional filters."""
        from sqlalchemy import func as sa_func
        query = select(sa_func.count(AuditLog.id)).where(AuditLog.organization_id == organization_id)

        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.where(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalar_one()
