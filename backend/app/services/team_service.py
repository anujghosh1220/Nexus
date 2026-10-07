from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, and_

from app.core.exceptions import (
    ResourceNotFoundError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from app.repositories.team_repository import TeamRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
)
from app.models.team import Team
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.services.audit_log_service import AuditLogService


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.team_repo = TeamRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.permission_service = PermissionService()
        self.audit_log_service = AuditLogService(db)

    async def create_team(
        self,
        team_data: TeamCreate,
        requesting_user_id: str,
    ) -> TeamResponse:
        """Create a new team."""
        org = await self.org_repo.get_by_id(team_data.organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(team_data.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TEAM_CREATE):
            raise AuthorizationError("You don't have permission to create teams in this organization")

        existing = await self.team_repo.get_by_name_in_organization(team_data.organization_id, team_data.name)
        if existing:
            raise ConflictError("Team with this name already exists in this organization")

        team = await self.team_repo.create(
            organization_id=team_data.organization_id,
            name=team_data.name,
            description=team_data.description,
            created_by=requesting_user_id,
        )

        await self.audit_log_service.create_audit_log(
            organization_id=team_data.organization_id,
            action="team.created",
            resource_type="team",
            resource_id=team.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return TeamResponse.model_validate(team)

    async def get_team(
        self,
        team_id: str,
        requesting_user_id: str,
    ) -> TeamResponse:
        """Get team by ID."""
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise ResourceNotFoundError("Team")

        membership = await self.org_repo.get_membership(team.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TEAM_VIEW):
            raise AuthorizationError("You don't have permission to view this team")

        return TeamResponse.model_validate(team)

    async def list_teams(
        self,
        organization_id: str,
        requesting_user_id: str,
    ) -> TeamListResponse:
        """List teams in an organization."""
        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TEAM_VIEW):
            raise AuthorizationError("You don't have permission to view teams in this organization")

        teams = await self.team_repo.list_by_organization(organization_id)

        return TeamListResponse(
            items=[TeamResponse.model_validate(t) for t in teams],
            total=len(teams),
        )

    async def update_team(
        self,
        team_id: str,
        team_data: TeamUpdate,
        requesting_user_id: str,
    ) -> TeamResponse:
        """Update team."""
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise ResourceNotFoundError("Team")

        membership = await self.org_repo.get_membership(team.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TEAM_UPDATE):
            raise AuthorizationError("You don't have permission to update this team")

        if team_data.name is not None and team_data.name != team.name:
            existing = await self.team_repo.get_by_name_in_organization(team.organization_id, team_data.name)
            if existing:
                raise ConflictError("Team with this name already exists in this organization")
            team.name = team_data.name

        if team_data.description is not None:
            team.description = team_data.description

        await self.team_repo.update(team)

        await self.audit_log_service.create_audit_log(
            organization_id=team.organization_id,
            action="team.updated",
            resource_type="team",
            resource_id=team.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return TeamResponse.model_validate(team)

    async def delete_team(
        self,
        team_id: str,
        requesting_user_id: str,
    ) -> None:
        """Delete team."""
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise ResourceNotFoundError("Team")

        membership = await self.org_repo.get_membership(team.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TEAM_DELETE):
            raise AuthorizationError("You don't have permission to delete this team")

        await self.team_repo.delete(team)

        await self.audit_log_service.create_audit_log(
            organization_id=team.organization_id,
            action="team.deleted",
            resource_type="team",
            resource_id=team.id,
            user_id=requesting_user_id,
            changes=None,
        )
