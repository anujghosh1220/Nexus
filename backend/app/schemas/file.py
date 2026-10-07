from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FileBase(BaseModel):
    filename: str
    content_type: str
    size: int


class FileCreate(BaseModel):
    organization_id: str = Field(..., min_length=1)


class FileResponse(FileBase):
    id: str
    organization_id: str
    uploaded_by: str
    storage_key: str
    checksum: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    items: list[FileResponse]
    total: int
