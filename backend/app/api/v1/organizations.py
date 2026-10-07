from fastapi import APIRouter, Depends, status
from typing import List

from app.api.deps import get_current_user
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    MembershipCreate,
    MembershipResponse,
)
from app.services.organization_service import OrganizationService
from app.models.user import User
from app.models.membership import Role
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/organizations", tags=["organizations"])


async def get_org_service(db: AsyncSession = Depends(get_db)) -> OrganizationService:
    """Get organization service instance."""
    return OrganizationService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new organization."""
    return await org_service.create_organization(org_data, current_user.id)


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """List all organizations the user is a member of."""
    return await org_service.list_user_organizations(current_user.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Get organization by ID."""
    return await org_service.get_organization(org_id, current_user.id)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Update organization."""
    return await org_service.update_organization(org_id, org_data, current_user.id)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Delete organization."""
    await org_service.delete_organization(org_id, current_user.id)


@router.post("/{org_id}/members", status_code=status.HTTP_201_CREATED, response_model=MembershipResponse)
async def invite_member(
    org_id: str,
    membership_data: MembershipCreate,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Invite a user to an organization."""
    return await org_service.invite_member(org_id, membership_data, current_user.id)


@router.post("/{org_id}/members/accept", response_model=MembershipResponse)
async def accept_invitation(
    org_id: str,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Accept an organization invitation."""
    return await org_service.accept_invitation(org_id, current_user.id)


@router.get("/{org_id}/members", response_model=List[MembershipResponse])
async def list_members(
    org_id: str,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """List all members of an organization."""
    return await org_service.list_members(org_id, current_user.id)


@router.patch("/{org_id}/members/{user_id}", response_model=MembershipResponse)
async def update_member_role(
    org_id: str,
    user_id: str,
    new_role: Role,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Update a member's role."""
    return await org_service.update_member_role(org_id, user_id, new_role, current_user.id)


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: str,
    user_id: str,
    org_service: OrganizationService = Depends(get_org_service),
    current_user: User = Depends(get_current_user),
):
    """Remove a member from an organization."""
    await org_service.remove_member(org_id, user_id, current_user.id)
