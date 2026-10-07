from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from app.models.task import Task, TaskStatus, TaskPriority


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        project_id: str,
        title: str,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        status: TaskStatus = TaskStatus.TODO,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            id=Task._generate_id(),
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            created_by=created_by,
            due_date=due_date,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        result = await self.db.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
    ) -> List[Task]:
        """List all tasks in a project."""
        result = await self.db.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, task: Task) -> Task:
        """Update task."""
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        """Delete task."""
        await self.db.delete(task)
        await self.db.flush()
