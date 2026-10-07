from fastapi import APIRouter, Depends, status
from typing import List

from app.api.deps import get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.services.project_service import ProjectService
from app.models.user import User
from app.models.membership import Membership, MembershipStatus
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.permission_service import PermissionService


router = APIRouter(prefix="/projects", tags=["projects"])


async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    """Get project service instance."""
    return ProjectService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    return await project_service.create_project(project_data, current_user.id)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    organization_id: str,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """List projects in an organization."""
    return await project_service.list_projects(organization_id, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """Get project by ID."""
    return await project_service.get_project(project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """Update project."""
    return await project_service.update_project(project_id, project_data, current_user.id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    """Delete project."""
    await project_service.delete_project(project_id, current_user.id)
