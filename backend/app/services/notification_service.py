from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import json

from app.repositories.notification_repository import NotificationRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.core.exceptions import AuthorizationError, ResourceNotFoundError


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()

    async def create_notification(
        self,
        user_id: str,
        organization_id: str,
        type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
    ) -> NotificationResponse:
        """Create a notification."""
        data_str = json.dumps(data) if data else None
        notification = await self.notification_repo.create(
            user_id=user_id,
            organization_id=organization_id,
            type=type,
            title=title,
            message=message,
            data=data_str,
        )
        return NotificationResponse.model_validate(notification)

    async def list_notifications(
        self,
        requesting_user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> NotificationListResponse:
        """List notifications for the current user."""
        notifications = await self.notification_repo.list_for_user(
            user_id=requesting_user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
        )
        unread_count = await self.notification_repo.count_for_user(
            user_id=requesting_user_id,
            unread_only=True,
        )

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifications],
            total=await self.notification_repo.count_for_user(requesting_user_id),
            unread_count=unread_count,
        )

    async def get_notification(
        self,
        notification_id: str,
        requesting_user_id: str,
    ) -> NotificationResponse:
        """Get notification by ID."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ResourceNotFoundError("Notification")

        if notification.user_id != requesting_user_id:
            raise AuthorizationError("You don't have permission to view this notification")

        return NotificationResponse.model_validate(notification)

    async def mark_notification_as_read(
        self,
        notification_id: str,
        requesting_user_id: str,
    ) -> NotificationResponse:
        """Mark notification as read."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ResourceNotFoundError("Notification")

        if notification.user_id != requesting_user_id:
            raise AuthorizationError("You don't have permission to update this notification")

        notification = await self.notification_repo.mark_as_read(notification)
        return NotificationResponse.model_validate(notification)

    async def mark_all_notifications_as_read(
        self,
        requesting_user_id: str,
    ) -> None:
        """Mark all notifications for a user as read."""
        await self.notification_repo.mark_all_as_read(requesting_user_id)

    async def notify_organization_members(
        self,
        organization_id: str,
        type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
        exclude_user_id: Optional[str] = None,
    ) -> List[NotificationResponse]:
        """Send notification to all organization members except excluded user."""
        memberships = await self.org_repo.get_organization_members(organization_id)
        notifications = []

        for membership in memberships:
            if membership.status != MembershipStatus.ACTIVE:
                continue
            if exclude_user_id and membership.user_id == exclude_user_id:
                continue

            notification = await self.create_notification(
                user_id=membership.user_id,
                organization_id=organization_id,
                type=type,
                title=title,
                message=message,
                data=data,
            )
            notifications.append(notification)

        return notifications
