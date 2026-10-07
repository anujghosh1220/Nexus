from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.core.exceptions import AuthorizationError, ResourceNotFoundError


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_log_repo = AuditLogRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()

    async def list_audit_logs(
        self,
        organization_id: str,
        requesting_user_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AuditLogListResponse:
        """List audit logs for an organization."""
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.AUDIT_LOG_VIEW):
            raise AuthorizationError("You don't have permission to view audit logs")

        logs = await self.audit_log_repo.list_by_organization(
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.audit_log_repo.count_by_organization(
            organization_id=organization_id,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
        )

        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(log) for log in logs],
            total=total,
        )

    async def create_audit_log(
        self,
        organization_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        changes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogResponse:
        """Create an audit log entry."""
        audit_log = await self.audit_log_repo.create(
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return AuditLogResponse.model_validate(audit_log)
