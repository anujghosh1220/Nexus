from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime
from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        organization_id: str,
        type: str,
        title: str,
        message: str,
        data: Optional[str] = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            id=Notification._generate_id(),
            user_id=user_id,
            organization_id=organization_id,
            type=type,
            title=title,
            message=message,
            data=data,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        """List notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.read_at.is_(None))

        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_for_user(self, user_id: str, unread_only: bool = False) -> int:
        """Count notifications for a user."""
        from sqlalchemy import func as sa_func
        query = select(sa_func.count(Notification.id)).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.read_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def mark_as_read(self, notification: Notification) -> Notification:
        """Mark notification as read."""
        if notification.read_at is None:
            notification.read_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: str) -> None:
        """Mark all notifications for a user as read."""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None)
                )
            )
        )
        notifications = result.scalars().all()
        now = datetime.utcnow()
        for notification in notifications:
            notification.read_at = now
        await self.db.flush()
