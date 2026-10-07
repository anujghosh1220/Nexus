from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
    AuthorizationError,
)
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    MembershipCreate,
    MembershipResponse,
)
from app.models.organization import Organization
from app.models.membership import Membership, Role, MembershipStatus
from app.models.user import User
from app.services.permission_service import PermissionService
from app.services.audit_log_service import AuditLogService


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()
        self.audit_log_service = AuditLogService(db)

    async def create_organization(
        self,
        org_data: OrganizationCreate,
        owner_id: str,
    ) -> OrganizationResponse:
        """Create a new organization."""
        # Check if slug is already taken
        existing = await self.org_repo.get_by_slug(org_data.slug)
        if existing:
            raise ConflictError("Organization slug already exists")

        # Verify owner exists
        owner = await self.user_repo.get_by_id(owner_id)
        if not owner:
            raise ResourceNotFoundError("User")

        # Create organization
        org = await self.org_repo.create(
            name=org_data.name,
            slug=org_data.slug,
            owner_id=owner_id,
            logo_url=org_data.logo_url,
        )

        await self.audit_log_service.create_audit_log(
            organization_id=org.id,
            action="organization.created",
            resource_type="organization",
            resource_id=org.id,
            user_id=owner_id,
            changes=None,
        )

        return OrganizationResponse.model_validate(org)

    async def get_organization(
        self,
        org_id: str,
        requesting_user_id: str,
    ) -> OrganizationResponse:
        """Get organization by ID (user must be a member)."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check if user is a member
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        return OrganizationResponse.model_validate(org)

    async def update_organization(
        self,
        org_id: str,
        org_data: OrganizationUpdate,
        requesting_user_id: str,
    ) -> OrganizationResponse:
        """Update organization (owner/admin only)."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check permissions using permission service
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.ORG_UPDATE):
            raise AuthorizationError("You don't have permission to update this organization")

        # Update fields
        if org_data.name is not None:
            org.name = org_data.name
        if org_data.logo_url is not None:
            org.logo_url = org_data.logo_url

        # If slug is being updated, check uniqueness
        if org_data.slug is not None and org_data.slug != org.slug:
            existing = await self.org_repo.get_by_slug(org_data.slug)
            if existing:
                raise ConflictError("Organization slug already exists")
            org.slug = org_data.slug

        await self.org_repo.update(org)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.updated",
            resource_type="organization",
            resource_id=org_id,
            user_id=requesting_user_id,
            changes=None,
        )

        return OrganizationResponse.model_validate(org)

    async def delete_organization(
        self,
        org_id: str,
        requesting_user_id: str,
    ) -> None:
        """Delete organization (owner only)."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check permissions using permission service
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.ORG_DELETE):
            raise AuthorizationError("Only the owner can delete an organization")

        await self.org_repo.delete(org)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.deleted",
            resource_type="organization",
            resource_id=org_id,
            user_id=requesting_user_id,
            changes=None,
        )

    async def list_user_organizations(
        self,
        user_id: str,
    ) -> List[OrganizationResponse]:
        """List all organizations the user is a member of."""
        memberships = await self.org_repo.get_user_memberships(user_id)

        orgs = []
        for membership in memberships:
            if membership.status == MembershipStatus.ACTIVE:
                org = await self.org_repo.get_by_id(membership.organization_id)
                if org:
                    orgs.append(OrganizationResponse.model_validate(org))

        return orgs

    async def invite_member(
        self,
        org_id: str,
        membership_data: MembershipCreate,
        requesting_user_id: str,
    ) -> MembershipResponse:
        """Invite a user to an organization (owner/admin only)."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check permissions using permission service
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.ORG_INVITE_MEMBERS):
            raise AuthorizationError("You don't have permission to invite members")

        # Find user by email
        user = await self.user_repo.get_by_email(membership_data.email)
        if not user:
            raise ResourceNotFoundError("User with this email")

        # Check if already a member
        existing = await self.org_repo.get_membership(org_id, user.id)
        if existing:
            raise ConflictError("User is already a member of this organization")

        # Create membership
        new_membership = await self.org_repo.create_membership(
            organization_id=org_id,
            user_id=user.id,
            role=membership_data.role,
        )

        # TODO: Send invitation email (background job)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.member_invited",
            resource_type="membership",
            resource_id=new_membership.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return MembershipResponse.model_validate(new_membership)

    async def accept_invitation(
        self,
        org_id: str,
        user_id: str,
    ) -> MembershipResponse:
        """Accept an organization invitation."""
        membership = await self.org_repo.get_membership(org_id, user_id)
        if not membership:
            raise ResourceNotFoundError("Invitation")

        if membership.status != MembershipStatus.PENDING:
            raise ConflictError("Invitation is not pending")

        await self.org_repo.accept_membership(membership)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.member_accepted",
            resource_type="membership",
            resource_id=membership.id,
            user_id=membership.user_id,
            changes=None,
        )

        return MembershipResponse.model_validate(membership)

    async def list_members(
        self,
        org_id: str,
        requesting_user_id: str,
    ) -> List[MembershipResponse]:
        """List all members of an organization."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check if user is a member
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        memberships = await self.org_repo.get_organization_members(org_id)

        return [MembershipResponse.model_validate(m) for m in memberships]

    async def update_member_role(
        self,
        org_id: str,
        user_id: str,
        new_role: Role,
        requesting_user_id: str,
    ) -> MembershipResponse:
        """Update a member's role (owner/admin only)."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check permissions using permission service
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.ORG_MANAGE_MEMBERS):
            raise AuthorizationError("You don't have permission to update member roles")

        # Cannot demote owner
        if org.owner_id == user_id:
            raise AuthorizationError("Cannot change the owner's role")

        # Get target membership
        target_membership = await self.org_repo.get_membership(org_id, user_id)
        if not target_membership:
            raise ResourceNotFoundError("Member")

        # Cannot promote to owner
        if new_role == Role.OWNER:
            raise AuthorizationError("Cannot promote to owner. Transfer ownership instead.")

        await self.org_repo.update_membership_role(target_membership, new_role)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.member_role_updated",
            resource_type="membership",
            resource_id=target_membership.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return MembershipResponse.model_validate(target_membership)

    async def remove_member(
        self,
        org_id: str,
        user_id: str,
        requesting_user_id: str,
    ) -> None:
        """Remove a member from an organization."""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        # Check permissions using permission service
        membership = await self.org_repo.get_membership(org_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.ORG_MANAGE_MEMBERS):
            raise AuthorizationError("You don't have permission to remove members")

        # Owner can remove anyone except themselves
        # Admin can remove members and managers (but not owners or other admins)
        target_membership = await self.org_repo.get_membership(org_id, user_id)
        if not target_membership:
            raise ResourceNotFoundError("Member")

        if membership.role == Role.OWNER:
            if org.owner_id == user_id:
                raise AuthorizationError("Owner cannot be removed. Transfer ownership first.")
        elif membership.role == Role.ADMIN:
            if target_membership.role in [Role.OWNER, Role.ADMIN]:
                raise AuthorizationError("You don't have permission to remove this member")

        await self.org_repo.delete_membership(target_membership)

        await self.audit_log_service.create_audit_log(
            organization_id=org_id,
            action="organization.member_removed",
            resource_type="membership",
            resource_id=target_membership.id,
            user_id=requesting_user_id,
            changes=None,
        )
