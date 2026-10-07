from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.membership import Role
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$")
    description: Optional[str] = Field(None, max_length=500)
    status: ProjectStatus = ProjectStatus.ACTIVE
    owner_id: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    organization_id: str = Field(..., min_length=1)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    key: Optional[str] = Field(None, min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$")
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
