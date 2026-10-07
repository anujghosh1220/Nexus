from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.membership import Role


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")


class OrganizationCreate(OrganizationBase):
    logo_url: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    logo_url: Optional[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    email: str
    role: Role = Role.MEMBER


class MembershipResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: Role
    status: str
    invited_at: datetime
    joined_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
