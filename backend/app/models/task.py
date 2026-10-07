from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string
import enum


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default=TaskStatus.TODO)
    priority = Column(String, nullable=False, default=TaskPriority.MEDIUM)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the task."""
        alphabet = string.ascii_letters + string.digits
        return "tsk_" + "".join(secrets.choice(alphabet) for _ in range(20))
