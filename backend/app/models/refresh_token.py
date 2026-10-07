from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.core.database import Base
import secrets
import string


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the refresh token."""
        alphabet = string.ascii_letters + string.digits
        return "rtk_" + "".join(secrets.choice(alphabet) for _ in range(20))
