from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.models.email_verification import EmailVerification
from datetime import datetime, timedelta
from app.core.security import get_password_hash


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> User:
        """Create a new user."""
        user = User(
            id=User._generate_id(),
            email=email,
            password_hash=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update user."""
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def verify_email(self, user: User) -> User:
        """Mark user email as verified."""
        user.is_verified = True
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def change_password(self, user: User, new_password: str) -> User:
        """Change user password."""
        user.password_hash = get_password_hash(new_password)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def deactivate(self, user: User) -> User:
        """Deactivate user account."""
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # Refresh Token methods
    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expires_delta: timedelta
    ) -> RefreshToken:
        """Create a refresh token."""
        refresh_token = RefreshToken(
            id=RefreshToken._generate_id(),
            token=token,
            user_id=user_id,
            expires_at=datetime.utcnow() + expires_delta,
        )
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string."""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == token,
                    RefreshToken.revoked_at.is_(None),
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: RefreshToken) -> RefreshToken:
        """Revoke a refresh token."""
        token.revoked_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(token)
        return token

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked_at.is_(None)
                )
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked_at = datetime.utcnow()
        await self.db.flush()

    # Password Reset Token methods
    async def create_password_reset_token(
        self,
        user_id: str,
        token: str,
        expires_delta: timedelta
    ) -> PasswordResetToken:
        """Create a password reset token."""
        reset_token = PasswordResetToken(
            id=PasswordResetToken._generate_id(),
            token=token,
            user_id=user_id,
            expires_at=datetime.utcnow() + expires_delta,
        )
        self.db.add(reset_token)
        await self.db.flush()
        await self.db.refresh(reset_token)
        return reset_token

    async def get_password_reset_token(self, token: str) -> Optional[PasswordResetToken]:
        """Get password reset token by token string."""
        result = await self.db.execute(
            select(PasswordResetToken).where(
                and_(
                    PasswordResetToken.token == token,
                    PasswordResetToken.used_at.is_(None),
                    PasswordResetToken.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()

    async def mark_password_reset_token_used(self, token: PasswordResetToken) -> PasswordResetToken:
        """Mark password reset token as used."""
        token.used_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(token)
        return token

    # Email Verification methods
    async def create_email_verification(
        self,
        user_id: str,
        token: str,
        expires_delta: timedelta
    ) -> EmailVerification:
        """Create an email verification token."""
        verification = EmailVerification(
            id=EmailVerification._generate_id(),
            token=token,
            user_id=user_id,
            expires_at=datetime.utcnow() + expires_delta,
        )
        self.db.add(verification)
        await self.db.flush()
        await self.db.refresh(verification)
        return verification

    async def get_email_verification(self, token: str) -> Optional[EmailVerification]:
        """Get email verification by token string."""
        result = await self.db.execute(
            select(EmailVerification).where(
                and_(
                    EmailVerification.token == token,
                    EmailVerification.verified_at.is_(None),
                    EmailVerification.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()

    async def mark_email_verified(self, verification: EmailVerification) -> EmailVerification:
        """Mark email verification as verified."""
        verification.verified_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(verification)
        return verification
