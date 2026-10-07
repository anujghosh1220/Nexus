from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_

from app.core.exceptions import (
    ResourceNotFoundError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.models.project import Project, ProjectStatus
from app.models.membership import Membership, MembershipStatus
from app.models.user import User
from app.services.permission_service import PermissionService
from app.services.audit_log_service import AuditLogService


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()
        self.audit_log_service = AuditLogService(db)

    async def create_project(
        self,
        project_data: ProjectCreate,
        requesting_user_id: str,
    ) -> ProjectResponse:
        """Create a new project."""
        # Verify organization exists and user is a member
        org = await self.org_repo.get_by_id(project_data.organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(project_data.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.PROJECT_CREATE):
            raise AuthorizationError("You don't have permission to create projects in this organization")

        # Verify owner exists
        owner_id = project_data.owner_id if project_data.owner_id else requesting_user_id
        owner = await self.user_repo.get_by_id(owner_id)
        if not owner:
            raise ResourceNotFoundError("User")

        # Verify owner is a member of the organization
        owner_membership = await self.org_repo.get_membership(project_data.organization_id, owner_id)
        if not owner_membership or owner_membership.status != MembershipStatus.ACTIVE:
            raise ValidationError("Project owner must be a member of the organization")

        # Check if project key already exists in organization
        existing = await self._get_by_key_in_org(project_data.organization_id, project_data.key)
        if existing:
            raise ConflictError("Project key already exists in this organization")

        # Create project
        project = await self.project_repo.create(
            organization_id=project_data.organization_id,
            name=project_data.name,
            key=project_data.key,
            owner_id=owner_id,
            description=project_data.description,
            status=project_data.status,
            start_date=project_data.start_date,
            due_date=project_data.due_date,
        )

        await self.audit_log_service.create_audit_log(
            organization_id=project_data.organization_id,
            action="project.created",
            resource_type="project",
            resource_id=project.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return ProjectResponse.model_validate(project)

    async def get_project(
        self,
        project_id: str,
        requesting_user_id: str,
    ) -> ProjectResponse:
        """Get project by ID."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        # Verify user is a member of the project's organization
        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        return ProjectResponse.model_validate(project)

    async def list_projects(
        self,
        organization_id: str,
        requesting_user_id: str,
    ) -> ProjectListResponse:
        """List projects in an organization."""
        # Verify user is a member
        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        projects = await self.project_repo.list_by_organization(organization_id)

        return ProjectListResponse(
            items=[ProjectResponse.model_validate(p) for p in projects],
            total=len(projects),
        )

    async def update_project(
        self,
        project_id: str,
        project_data: ProjectUpdate,
        requesting_user_id: str,
    ) -> ProjectResponse:
        """Update project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        # Verify user is a member of the project's organization
        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.PROJECT_UPDATE):
            raise AuthorizationError("You don't have permission to update this project")

        # Update fields
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        if project_data.status is not None:
            project.status = project_data.status
        if project_data.start_date is not None:
            project.start_date = project_data.start_date
        if project_data.due_date is not None:
            project.due_date = project_data.due_date

        # If key is being updated, check uniqueness
        if project_data.key is not None and project_data.key != project.key:
            existing = await self._get_by_key_in_org(project.organization_id, project_data.key)
            if existing:
                raise ConflictError("Project key already exists in this organization")
            project.key = project_data.key

        await self.project_repo.update(project)

        await self.audit_log_service.create_audit_log(
            organization_id=project.organization_id,
            action="project.updated",
            resource_type="project",
            resource_id=project.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return ProjectResponse.model_validate(project)

    async def delete_project(
        self,
        project_id: str,
        requesting_user_id: str,
    ) -> None:
        """Delete project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        # Verify user is a member of the project's organization
        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.PROJECT_DELETE):
            raise AuthorizationError("You don't have permission to delete this project")

        await self.project_repo.delete(project)

        await self.audit_log_service.create_audit_log(
            organization_id=project.organization_id,
            action="project.deleted",
            resource_type="project",
            resource_id=project.id,
            user_id=requesting_user_id,
            changes=None,
        )

    async def _get_by_key_in_org(self, organization_id: str, key: str) -> Optional[Project]:
        """Get project by key within an organization."""
        result = await self.db.execute(
            select(Project).where(
                and_(
                    Project.organization_id == organization_id,
                    Project.key == key,
                )
            )
        )
        return result.scalar_one_or_none()
