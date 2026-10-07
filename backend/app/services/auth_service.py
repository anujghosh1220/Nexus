from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import pyotp
from fastapi import status

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    create_2fa_token,
    decode_2fa_token,
    decode_token,
    generate_token,
    generate_totp_secret,
    verify_totp,
)
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from app.schemas.two_factor import (
    TwoFactorSetupResponse,
    TwoFactorVerifyResponse,
    TwoFactorStatusResponse,
)
from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user and return tokens."""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError("User with this email already exists")

        # Validate password strength
        self._validate_password(user_data.password)

        # Create user
        user = await self.user_repo.create(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        # Create tokens
        return await self._create_tokens(user)

    async def login(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens."""
        # Get user by email
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            raise AuthenticationError("Invalid credentials")

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Check if 2FA is enabled
        if user.totp_enabled:
            # Return 2FA challenge token instead of full tokens
            return TokenResponse(
                access_token=create_2fa_token(user.id),
                refresh_token="",
                requires_2fa=True,
                user=UserResponse.model_validate(user),
            )

        # Update last login
        await self.user_repo.update_last_login(user)

        # Create tokens
        return await self._create_tokens(user)

    async def verify_2fa(self, user_id: str, token: str) -> TokenResponse:
        """Verify 2FA token and return full authentication tokens."""
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        if not user.totp_enabled or not user.totp_secret:
            raise AuthenticationError("2FA is not enabled for this user")

        # Verify TOTP token
        if not verify_totp(user.totp_secret, token):
            raise AuthenticationError("Invalid 2FA token", status_code=status.HTTP_400_BAD_REQUEST)

        # Update last login
        await self.user_repo.update_last_login(user)

        # Create tokens
        return await self._create_tokens(user)

    async def setup_2fa(self, user_id: str) -> TwoFactorSetupResponse:
        """Setup 2FA for user - generates secret but does not enable."""
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if user.totp_enabled:
            raise ValidationError("2FA is already enabled")

        # Generate new TOTP secret
        secret = generate_totp_secret()

        # Store secret temporarily (not enabled yet)
        user.totp_secret = secret
        await self.user_repo.update(user)

        # Generate provisioning URI
        totp = pyotp.TOTP(secret)
        qr_code_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="NEXUS"
        )

        return TwoFactorSetupResponse(
            secret=secret,
            qr_code_uri=qr_code_uri,
            issuer="NEXUS",
            account=user.email,
        )

    async def enable_2fa(self, user_id: str, token: str) -> TokenResponse:
        """Enable 2FA after verifying token."""
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if not user.totp_secret:
            raise ValidationError("2FA setup not initiated")

        if user.totp_enabled:
            raise ValidationError("2FA is already enabled")

        # Verify TOTP token
        if not verify_totp(user.totp_secret, token):
            raise AuthenticationError("Invalid 2FA token", status_code=status.HTTP_400_BAD_REQUEST)

        # Enable 2FA
        user.totp_enabled = True
        await self.user_repo.update(user)

        # Create tokens
        return await self._create_tokens(user)

    async def disable_2fa(self, user_id: str, password: str) -> None:
        """Disable 2FA for user."""
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if not user.totp_enabled:
            raise ValidationError("2FA is not enabled")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid password", status_code=status.HTTP_400_BAD_REQUEST)

        # Disable 2FA
        user.totp_enabled = False
        user.totp_secret = None
        await self.user_repo.update(user)

    async def get_2fa_status(self, user_id: str) -> TwoFactorStatusResponse:
        """Get 2FA status for user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        return TwoFactorStatusResponse(enabled=user.totp_enabled)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Get refresh token from database
        token_record = await self.user_repo.get_refresh_token(refresh_token)
        if not token_record:
            raise AuthenticationError("Invalid or expired refresh token")

        # Get user
        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Revoke old refresh token (token rotation)
        await self.user_repo.revoke_refresh_token(token_record)

        # Create new tokens
        return await self._create_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        """Logout user by revoking refresh token."""
        token_record = await self.user_repo.get_refresh_token(refresh_token)
        if token_record:
            await self.user_repo.revoke_refresh_token(token_record)

    async def logout_all(self, user_id: str) -> None:
        """Logout user from all devices by revoking all refresh tokens."""
        await self.user_repo.revoke_all_user_tokens(user_id)

    async def verify_email_token(self, token: str) -> UserResponse:
        """Verify email using verification token."""
        verification = await self.user_repo.get_email_verification(token)
        if not verification:
            raise ValidationError("Invalid or expired verification token")

        # Get user
        user = await self.user_repo.get_by_id(verification.user_id)
        if not user:
            raise ValidationError("User not found")

        # Mark as verified
        await self.user_repo.verify_email(user)
        await self.user_repo.mark_email_verified(verification)

        return UserResponse.model_validate(user)

    async def request_password_reset(self, email: str) -> None:
        """Request password reset."""
        # Get user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal whether email exists
            return

        # Create reset token
        token = generate_token()
        await self.user_repo.create_password_reset_token(
            user_id=user.id,
            token=token,
            expires_delta=timedelta(hours=1),
        )

        # TODO: Send email with reset link (background job)
        # For now, just log that a reset was requested (do NOT log the token itself)
        from app.core.logging import logger
        logger.info(f"Password reset requested for {email}")

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password using reset token."""
        # Validate password strength
        self._validate_password(new_password)

        # Get reset token
        reset_token = await self.user_repo.get_password_reset_token(token)
        if not reset_token:
            raise ValidationError("Invalid or expired reset token")

        # Get user
        user = await self.user_repo.get_by_id(reset_token.user_id)
        if not user:
            raise ValidationError("User not found")

        # Change password
        await self.user_repo.change_password(user, new_password)
        await self.user_repo.mark_password_reset_token_used(reset_token)

        # Revoke all refresh tokens (force re-login)
        await self.user_repo.revoke_all_user_tokens(user.id)

    async def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        payload = decode_token(token, settings.JWT_SECRET)
        if not payload:
            raise AuthenticationError("Invalid token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User is inactive")

        return user

    async def get_current_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID without token validation."""
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return user

    async def _create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user."""
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
        )

        # Create refresh token
        refresh_token_str = generate_token()
        await self.user_repo.create_refresh_token(
            user_id=user.id,
            token=refresh_token_str,
            expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user=UserResponse.model_validate(user),
        )

    def _validate_password(self, password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        # Add more validation as needed
        # For now, just check length
