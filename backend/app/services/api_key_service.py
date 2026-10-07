from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import json

from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse, ApiKeyListResponse
from app.models.membership import Membership, MembershipStatus
from app.services.permission_service import PermissionService
from app.core.exceptions import AuthorizationError, ResourceNotFoundError, ConflictError, ValidationError
from app.core.security import hash_api_key, generate_token


class ApiKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key_repo = ApiKeyRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)
        self.permission_service = PermissionService()

    async def create_api_key(
        self,
        organization_id: str,
        requesting_user_id: str,
        name: str,
        scopes: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
    ) -> ApiKeyCreateResponse:
        """Create a new API key."""
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.API_KEY_CREATE):
            raise AuthorizationError("You don't have permission to create API keys")

        user = await self.user_repo.get_by_id(requesting_user_id)
        if not user:
            raise ResourceNotFoundError("User")

        # Generate secure API key
        secret = generate_token(32)
        full_key = f"nx_live_{secret}"
        key_prefix = full_key[:12]
        key_hash = hash_api_key(full_key)
        scopes_str = json.dumps(scopes) if scopes else None

        api_key = await self.api_key_repo.create(
            organization_id=organization_id,
            created_by=requesting_user_id,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=scopes_str,
            expires_at=expires_at,
        )

        return ApiKeyCreateResponse(
            id=api_key.id,
            organization_id=api_key.organization_id,
            created_by=api_key.created_by,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            scopes=scopes,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            revoked_at=api_key.revoked_at,
            created_at=api_key.created_at,
            key=full_key,
        )

    async def list_api_keys(
        self,
        organization_id: str,
        requesting_user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> ApiKeyListResponse:
        """List API keys for an organization."""
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ResourceNotFoundError("Organization")

        membership = await self.org_repo.get_membership(organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.API_KEY_VIEW):
            raise AuthorizationError("You don't have permission to view API keys")

        keys = await self.api_key_repo.list_by_organization(organization_id, limit, offset)
        total = await self.api_key_repo.count_by_organization(organization_id)

        return ApiKeyListResponse(
            items=[ApiKeyResponse.model_validate(k) for k in keys],
            total=total,
        )

    async def get_api_key(
        self,
        api_key_id: str,
        requesting_user_id: str,
    ) -> ApiKeyResponse:
        """Get API key by ID."""
        api_key = await self.api_key_repo.get_by_id(api_key_id)
        if not api_key:
            raise ResourceNotFoundError("API key")

        membership = await self.org_repo.get_membership(api_key.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.API_KEY_VIEW):
            raise AuthorizationError("You don't have permission to view API keys")

        return ApiKeyResponse.model_validate(api_key)

    async def revoke_api_key(
        self,
        api_key_id: str,
        requesting_user_id: str,
    ) -> ApiKeyResponse:
        """Revoke an API key."""
        api_key = await self.api_key_repo.get_by_id(api_key_id)
        if not api_key:
            raise ResourceNotFoundError("API key")

        membership = await self.org_repo.get_membership(api_key.organization_id, requesting_user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise AuthorizationError("You are not a member of this organization")

        if not self.permission_service.has_permission(membership.role, PermissionService.API_KEY_REVOKE):
            raise AuthorizationError("You don't have permission to revoke API keys")

        if api_key.revoked_at is not None:
            return ApiKeyResponse.model_validate(api_key)

        api_key = await self.api_key_repo.revoke(api_key)
        return ApiKeyResponse.model_validate(api_key)

    async def authenticate_api_key(self, full_key: str) -> Optional[dict]:
        """Authenticate an API key and return context."""
        key_hash = hash_api_key(full_key)
        key_prefix = full_key[:12]

        api_key = await self.api_key_repo.get_by_prefix(key_prefix)
        if not api_key:
            return None

        if api_key.key_hash != key_hash:
            return None

        if api_key.revoked_at is not None:
            return None

        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None

        await self.api_key_repo.update_last_used(api_key)

        scopes = []
        if api_key.scopes:
            try:
                scopes = json.loads(api_key.scopes)
            except json.JSONDecodeError:
                pass

        return {
            "id": api_key.id,
            "organization_id": api_key.organization_id,
            "created_by": api_key.created_by,
            "scopes": scopes,
            "key_name": api_key.name,
        }
