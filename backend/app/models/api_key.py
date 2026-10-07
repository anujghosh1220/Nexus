from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    scopes = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the API key."""
        alphabet = string.ascii_letters + string.digits
        return "key_" + "".join(secrets.choice(alphabet) for _ in range(20))
