from fastapi import APIRouter, Depends, status
from typing import List

from app.api.deps import get_current_user
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.services.task_service import TaskService
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """Get task service instance."""
    return TaskService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    return await task_service.create_task(task_data, current_user.id)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    project_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """List tasks in a project."""
    return await task_service.list_tasks(project_id, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Get task by ID."""
    return await task_service.get_task(task_id, current_user.id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Update task."""
    return await task_service.update_task(task_id, task_data, current_user.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    """Delete task."""
    await task_service.delete_task(task_id, current_user.id)
