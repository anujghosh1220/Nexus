from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(Text, nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the notification."""
        alphabet = string.ascii_letters + string.digits
        return "not_" + "".join(secrets.choice(alphabet) for _ in range(20))
