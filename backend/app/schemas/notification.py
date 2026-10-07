from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class NotificationBase(BaseModel):
    type: str
    title: str
    message: str
    data: Optional[str] = None


class NotificationCreate(NotificationBase):
    user_id: str
    organization_id: str


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    organization_id: str
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int
