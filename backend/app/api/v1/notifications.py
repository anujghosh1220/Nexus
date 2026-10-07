from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_current_user
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse
from app.services.notification_service import NotificationService
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    """Get notification service instance."""
    return NotificationService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
):
    """Create a notification."""
    return await notification_service.create_notification(
        user_id=notification_data.user_id,
        organization_id=notification_data.organization_id,
        type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        data=notification_data.data,
    )


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
):
    """List notifications for the current user."""
    return await notification_service.list_notifications(
        requesting_user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
):
    """Get notification by ID."""
    return await notification_service.get_notification(notification_id, current_user.id)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
):
    """Mark notification as read."""
    return await notification_service.mark_notification_as_read(notification_id, current_user.id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_notifications_as_read(
    notification_service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    await notification_service.mark_all_notifications_as_read(current_user.id)
