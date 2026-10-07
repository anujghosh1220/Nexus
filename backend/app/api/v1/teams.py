from fastapi import APIRouter, Depends, status
from typing import List

from app.api.deps import get_current_user
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
)
from app.services.team_service import TeamService
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/teams", tags=["teams"])


async def get_team_service(db: AsyncSession = Depends(get_db)) -> TeamService:
    """Get team service instance."""
    return TeamService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    team_service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new team."""
    return await team_service.create_team(team_data, current_user.id)


@router.get("", response_model=TeamListResponse)
async def list_teams(
    organization_id: str,
    team_service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    """List teams in an organization."""
    return await team_service.list_teams(organization_id, current_user.id)


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    team_service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    """Get team by ID."""
    return await team_service.get_team(team_id, current_user.id)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    team_service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    """Update team."""
    return await team_service.update_team(team_id, team_data, current_user.id)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    team_service: TeamService = Depends(get_team_service),
    current_user: User = Depends(get_current_user),
):
    """Delete team."""
    await team_service.delete_team(team_id, current_user.id)
