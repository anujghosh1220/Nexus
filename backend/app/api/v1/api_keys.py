from fastapi import APIRouter, Depends, status, Query

from app.api.deps import get_current_user, get_api_key_service
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse, ApiKeyListResponse
from app.services.api_key_service import ApiKeyService
from app.models.user import User

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiKeyCreateResponse)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new API key."""
    return await api_key_service.create_api_key(
        organization_id=api_key_data.organization_id,
        requesting_user_id=current_user.id,
        name=api_key_data.name,
        scopes=api_key_data.scopes,
        expires_at=api_key_data.expires_at,
    )


@router.get("", response_model=ApiKeyListResponse)
async def list_api_keys(
    organization_id: str = Query(...),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
    current_user: User = Depends(get_current_user),
):
    """List API keys for an organization."""
    return await api_key_service.list_api_keys(
        organization_id=organization_id,
        requesting_user_id=current_user.id,
    )


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    api_key_id: str,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
    current_user: User = Depends(get_current_user),
):
    """Get API key by ID."""
    return await api_key_service.get_api_key(api_key_id, current_user.id)


@router.post("/{api_key_id}/revoke", response_model=ApiKeyResponse)
async def revoke_api_key(
    api_key_id: str,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
    current_user: User = Depends(get_current_user),
):
    """Revoke an API key."""
    return await api_key_service.revoke_api_key(api_key_id, current_user.id)
