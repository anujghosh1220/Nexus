from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets
import string


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=False, unique=True, index=True)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for the file."""
        alphabet = string.ascii_letters + string.digits
        return "fil_" + "".join(secrets.choice(alphabet) for _ in range(20))

    @staticmethod
    def generate_storage_key(original_filename: str) -> str:
        """Generate a safe storage key."""
        alphabet = string.ascii_letters + string.digits
        random_part = "".join(secrets.choice(alphabet) for _ in range(32))
        ext = ""
        if "." in original_filename:
            ext = "." + original_filename.rsplit(".", 1)[-1].lower()
        return f"{random_part}{ext}"
