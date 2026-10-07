from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
import enum
import secrets
import string
from app.core.database import Base


class Role(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class MembershipStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(Role), nullable=False, default=Role.MEMBER)
    status = Column(SQLEnum(MembershipStatus), nullable=False, default=MembershipStatus.PENDING)
    invited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the membership."""
        alphabet = string.ascii_letters + string.digits
        return "mem_" + "".join(secrets.choice(alphabet) for _ in range(20))
