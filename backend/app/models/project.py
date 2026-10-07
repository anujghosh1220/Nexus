from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string
import enum


class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    ON_HOLD = "ON_HOLD"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False)  # e.g., "NEX", "ENG"
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default=ProjectStatus.ACTIVE)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    owner = relationship("User")
    tasks = relationship("Task", back_populates="project")

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the project."""
        alphabet = string.ascii_letters + string.digits
        return "prj_" + "".join(secrets.choice(alphabet) for _ in range(20))
