from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_auth_service, get_current_user
from app.schemas.audit_log import AuditLogListResponse
from app.services.audit_log_service import AuditLogService
from app.models.user import User
from app.core.database import get_db


router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


async def get_audit_log_service(db: AsyncSession = Depends(get_db)) -> AuditLogService:
    """Get audit log service instance."""
    return AuditLogService(db)


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    organization_id: str = Query(...),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    audit_log_service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(get_current_user),
):
    """List audit logs for an organization."""
    return await audit_log_service.list_audit_logs(
        organization_id=organization_id,
        requesting_user_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
