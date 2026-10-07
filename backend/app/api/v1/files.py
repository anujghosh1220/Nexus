from fastapi import APIRouter, Depends, status, Query, UploadFile, File as FastAPIFile, Form
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.schemas.file import FileCreate, FileResponse, FileListResponse
from app.services.file_service import FileService
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
import io

router = APIRouter(prefix="/files", tags=["files"])


async def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    """Get file service instance."""
    return FileService(db)


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=FileResponse)
async def upload_file(
    organization_id: str = Form(...),
    file: UploadFile = FastAPIFile(...),
    file_service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """Upload a file."""
    content = await file.read()
    return await file_service.upload_file(
        organization_id=organization_id,
        requesting_user_id=current_user.id,
        file_data=content,
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
    )


@router.get("", response_model=FileListResponse)
async def list_files(
    organization_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    file_service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """List files for an organization."""
    return await file_service.list_files(
        organization_id=organization_id,
        requesting_user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """Get file metadata by ID."""
    return await file_service.get_file(file_id, current_user.id)


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """Download a file."""
    data, content_type, filename = await file_service.download_file(file_id, current_user.id)
    return StreamingResponse(
        io.BytesIO(data),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """Delete a file."""
    await file_service.delete_file(file_id, current_user.id)
