from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, and_

from app.core.exceptions import (
    ResourceNotFoundError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.services.audit_log_service import AuditLogService


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()
        self.audit_log_service = AuditLogService(db)

    async def create_task(
        self,
        task_data: TaskCreate,
        requesting_user_id: str,
    ) -> TaskResponse:
        """Create a new task."""
        # Verify project exists
        project = await self.project_repo.get_by_id(task_data.project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        # Verify user is a member of the project's organization
        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TASK_CREATE):
            raise AuthorizationError("You don't have permission to create tasks in this project")

        # Verify assignee exists and is a member of the organization if provided
        assignee_id = task_data.assignee_id
        if assignee_id:
            assignee = await self.user_repo.get_by_id(assignee_id)
            if not assignee:
                raise ResourceNotFoundError("Assignee")

            assignee_membership = await self.org_repo.get_membership(project.organization_id, assignee_id)
            if not assignee_membership or assignee_membership.status != MembershipStatus.ACTIVE:
                raise ValidationError("Assignee must be a member of the project's organization")

        # Create task
        task = await self.task_repo.create(
            project_id=task_data.project_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            assignee_id=assignee_id,
            created_by=requesting_user_id,
            due_date=task_data.due_date,
        )

        await self.audit_log_service.create_audit_log(
            organization_id=project.organization_id,
            action="task.created",
            resource_type="task",
            resource_id=task.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return TaskResponse.model_validate(task)

    async def get_task(
        self,
        task_id: str,
        requesting_user_id: str,
    ) -> TaskResponse:
        """Get task by ID."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        # Verify user is a member of the task's project organization
        project = await self.project_repo.get_by_id(task.project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TASK_VIEW):
            raise AuthorizationError("You don't have permission to view this task")

        return TaskResponse.model_validate(task)

    async def list_tasks(
        self,
        project_id: str,
        requesting_user_id: str,
    ) -> TaskListResponse:
        """List tasks in a project."""
        # Verify project exists
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        # Verify user is a member of the project's organization
        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TASK_VIEW):
            raise AuthorizationError("You don't have permission to view tasks in this project")

        tasks = await self.task_repo.list_by_project(project_id)

        return TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=len(tasks),
        )

    async def update_task(
        self,
        task_id: str,
        task_data: TaskUpdate,
        requesting_user_id: str,
    ) -> TaskResponse:
        """Update task."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        # Verify user is a member of the task's project organization
        project = await self.project_repo.get_by_id(task.project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TASK_UPDATE):
            raise AuthorizationError("You don't have permission to update this task")

        # If assignee is being updated, verify assignee exists and is a member
        if task_data.assignee_id is not None and task_data.assignee_id != task.assignee_id:
            if task_data.assignee_id:
                assignee = await self.user_repo.get_by_id(task_data.assignee_id)
                if not assignee:
                    raise ResourceNotFoundError("Assignee")

                assignee_membership = await self.org_repo.get_membership(project.organization_id, task_data.assignee_id)
                if not assignee_membership or assignee_membership.status != MembershipStatus.ACTIVE:
                    raise ValidationError("Assignee must be a member of the project's organization")

        # Update fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.status is not None:
            task.status = task_data.status
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.assignee_id is not None:
            task.assignee_id = task_data.assignee_id
        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        await self.task_repo.update(task)

        await self.audit_log_service.create_audit_log(
            organization_id=project.organization_id,
            action="task.updated",
            resource_type="task",
            resource_id=task.id,
            user_id=requesting_user_id,
            changes=None,
        )

        return TaskResponse.model_validate(task)

    async def delete_task(
        self,
        task_id: str,
        requesting_user_id: str,
    ) -> None:
        """Delete task."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        # Verify user is a member of the task's project organization
        project = await self.project_repo.get_by_id(task.project_id)
        if not project:
            raise ResourceNotFoundError("Project")

        membership = await self.org_repo.get_membership(project.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.TASK_DELETE):
            raise AuthorizationError("You don't have permission to delete this task")

        await self.task_repo.delete(task)

        await self.audit_log_service.create_audit_log(
            organization_id=project.organization_id,
            action="task.deleted",
            resource_type="task",
            resource_id=task_id,
            user_id=requesting_user_id,
            changes=None,
        )
