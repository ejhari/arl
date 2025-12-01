"""Project permission models"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class ProjectRole(str, enum.Enum):
    """Project access roles"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectPermission(Base):
    """Project-level permissions for users"""

    __tablename__ = "project_permissions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(ProjectRole), nullable=False, default=ProjectRole.VIEWER)
    granted_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
