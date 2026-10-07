from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_auth_service, get_current_user, get_current_user_or_api_key
from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.rate_limit import limiter
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user."""
    return await auth_service.register(user_data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login with email and password."""
    return await auth_service.login(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    return await auth_service.refresh_tokens(token_data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Logout user."""
    await auth_service.logout(token_data.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Logout user from all devices."""
    await auth_service.logout_all(current_user.id)


@router.post("/verify-email", response_model=UserResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Verify email address."""
    return await auth_service.verify_email_token(verification_data.token)


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute")
async def request_password_reset(
    request: Request,
    request_data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request password reset email."""
    await auth_service.request_password_reset(request_data.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Reset password using reset token."""
    await auth_service.reset_password(reset_data.token, reset_data.new_password)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user_or_api_key),
):
    """Get current user information."""
    return UserResponse.model_validate(current_user)
