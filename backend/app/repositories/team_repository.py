from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.team import Team


class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: str,
        name: str,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Team:
        """Create a new team."""
        team = Team(
            id=Team._generate_id(),
            organization_id=organization_id,
            name=name,
            description=description,
            created_by=created_by,
        )
        self.db.add(team)
        await self.db.flush()
        await self.db.refresh(team)
        return team

    async def get_by_id(self, team_id: str) -> Optional[Team]:
        """Get team by ID."""
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: str,
    ) -> List[Team]:
        """List all teams in an organization."""
        result = await self.db.execute(
            select(Team)
            .where(Team.organization_id == organization_id)
            .order_by(Team.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_name_in_organization(
        self,
        organization_id: str,
        name: str,
    ) -> Optional[Team]:
        """Get team by name within an organization."""
        result = await self.db.execute(
            select(Team).where(
                and_(
                    Team.organization_id == organization_id,
                    Team.name == name,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, team: Team) -> Team:
        """Update team."""
        await self.db.flush()
        await self.db.refresh(team)
        return team

    async def delete(self, team: Team) -> None:
        """Delete team."""
        await self.db.delete(team)
        await self.db.flush()
