from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.api_key_service import ApiKeyService
from app.models.user import User
from app.repositories.user_repository import UserRepository


security = HTTPBearer(auto_error=False)


async def get_auth_service(
    db: AsyncSession = Depends(get_db)
) -> AuthService:
    """Get auth service instance."""
    return AuthService(db)


async def get_api_key_service(
    db: AsyncSession = Depends(get_db)
) -> ApiKeyService:
    """Get API key service instance."""
    return ApiKeyService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user_or_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> User:
    """Get current authenticated user via JWT or API key."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    token = credentials.credentials
    
    # Try JWT first
    try:
        user = await auth_service.get_current_user(token)
        return user
    except Exception:
        pass
    
    # Try API key
    try:
        api_key_context = await api_key_service.authenticate_api_key(token)
        if api_key_context:
            user_repo = UserRepository(api_key_service.db)
            user = await user_repo.get_by_id(api_key_context["created_by"])
            if user:
                return user
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
