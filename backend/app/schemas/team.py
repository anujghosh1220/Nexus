from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamCreate(TeamBase):
    organization_id: str = Field(..., min_length=1)


class TeamUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamResponse(TeamBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    items: list[TeamResponse]
    total: int
