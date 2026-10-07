from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.project import Project, ProjectStatus
from app.models.membership import MembershipStatus


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: str,
        name: str,
        key: str,
        owner_id: str,
        description: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.ACTIVE,
        start_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            id=Project._generate_id(),
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
            status=status,
            owner_id=owner_id,
            start_date=start_date,
            due_date=due_date,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: str,
    ) -> List[Project]:
        """List all projects in an organization."""
        result = await self.db.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, project: Project) -> Project:
        """Update project."""
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        """Delete project."""
        await self.db.delete(project)
        await self.db.flush()
