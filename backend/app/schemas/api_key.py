from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ApiKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class ApiKeyCreate(ApiKeyBase):
    organization_id: str = Field(..., min_length=1)


class ApiKeyResponse(ApiKeyBase):
    id: str
    organization_id: str
    created_by: str
    key_prefix: str
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    revoked_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(ApiKeyResponse):
    key: str


class ApiKeyListResponse(BaseModel):
    items: List[ApiKeyResponse]
    total: int
