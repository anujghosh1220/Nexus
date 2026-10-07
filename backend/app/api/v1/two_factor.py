from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service, get_current_user
from app.schemas.two_factor import (
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    TwoFactorVerifyResponse,
    TwoFactorDisableRequest,
    TwoFactorStatusResponse,
)
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.rate_limit import limiter
from app.core.config import settings
from app.core.security import decode_2fa_token
from app.core.exceptions import AuthenticationError

router = APIRouter(prefix="/2fa", tags=["2fa"])


@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Setup 2FA for current user."""
    return await auth_service.setup_2fa(current_user.id)


@router.post("/enable", response_model=TwoFactorVerifyResponse)
async def enable_2fa(
    verify_data: TwoFactorVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Enable 2FA after verifying token."""
    return await auth_service.enable_2fa(current_user.id, verify_data.token)


@router.post("/verify", response_model=TwoFactorVerifyResponse)
async def verify_2fa(
    request: Request,
    verify_data: TwoFactorVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify 2FA token and complete login."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError("Missing 2FA token")
    
    token = auth_header.split(" ")[1]
    payload = decode_2fa_token(token)
    if not payload:
        raise AuthenticationError("Invalid 2FA token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid 2FA token")
    
    return await auth_service.verify_2fa(user_id, verify_data.token)


@router.post("/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_2fa(
    disable_data: TwoFactorDisableRequest,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Disable 2FA for current user."""
    await auth_service.disable_2fa(current_user.id, disable_data.password)


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Get 2FA status for current user."""
    return await auth_service.get_2fa_status(current_user.id)
