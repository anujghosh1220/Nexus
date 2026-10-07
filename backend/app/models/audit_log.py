from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    changes = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the audit log."""
        alphabet = string.ascii_letters + string.digits
        return "aud_" + "".join(secrets.choice(alphabet) for _ in range(20))
