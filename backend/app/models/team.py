from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="teams")

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the team."""
        alphabet = string.ascii_letters + string.digits
        return "tm_" + "".join(secrets.choice(alphabet) for _ in range(20))
