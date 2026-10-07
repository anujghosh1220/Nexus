from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.organization import Organization
from app.models.membership import Membership, Role, MembershipStatus
from app.models.user import User
from datetime import datetime


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        slug: str,
        owner_id: str,
        logo_url: Optional[str] = None,
    ) -> Organization:
        """Create a new organization."""
        org = Organization(
            id=Organization._generate_id(),
            name=name,
            slug=slug,
            owner_id=owner_id,
            logo_url=logo_url,
        )
        self.db.add(org)
        await self.db.flush()
        await self.db.refresh(org)

        # Create owner membership
        membership = Membership(
            id=Membership._generate_id(),
            organization_id=org.id,
            user_id=owner_id,
            role=Role.OWNER,
            status=MembershipStatus.ACTIVE,
            joined_at=datetime.utcnow(),
        )
        self.db.add(membership)
        await self.db.flush()

        return org

    async def get_by_id(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        result = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: str) -> List[Organization]:
        """Get all organizations owned by a user."""
        result = await self.db.execute(
            select(Organization).where(Organization.owner_id == owner_id)
        )
        return result.scalars().all()

    async def update(self, org: Organization) -> Organization:
        """Update organization."""
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def delete(self, org: Organization) -> None:
        """Delete organization."""
        await self.db.delete(org)
        await self.db.flush()

    # Membership methods
    async def get_membership(
        self,
        organization_id: str,
        user_id: str,
    ) -> Optional[Membership]:
        """Get membership by organization and user."""
        result = await self.db.execute(
            select(Membership).where(
                and_(
                    Membership.organization_id == organization_id,
                    Membership.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_memberships(self, user_id: str) -> List[Membership]:
        """Get all memberships for a user."""
        result = await self.db.execute(
            select(Membership)
            .where(Membership.user_id == user_id)
            .order_by(Membership.created_at.desc())
        )
        return result.scalars().all()

    async def get_organization_members(
        self,
        organization_id: str,
    ) -> List[Membership]:
        """Get all members of an organization."""
        result = await self.db.execute(
            select(Membership)
            .where(Membership.organization_id == organization_id)
            .order_by(Membership.created_at.desc())
        )
        return result.scalars().all()

    async def create_membership(
        self,
        organization_id: str,
        user_id: str,
        role: Role = Role.MEMBER,
    ) -> Membership:
        """Create a new membership."""
        membership = Membership(
            id=Membership._generate_id(),
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            status=MembershipStatus.PENDING,
        )
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def update_membership_role(
        self,
        membership: Membership,
        new_role: Role,
    ) -> Membership:
        """Update membership role."""
        membership.role = new_role
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def accept_membership(self, membership: Membership) -> Membership:
        """Accept a pending membership."""
        membership.status = MembershipStatus.ACTIVE
        membership.joined_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def deactivate_membership(self, membership: Membership) -> Membership:
        """Deactivate a membership."""
        membership.status = MembershipStatus.INACTIVE
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def delete_membership(self, membership: Membership) -> None:
        """Delete a membership."""
        await self.db.delete(membership)
        await self.db.flush()
