"""Permission schemas for request/response validation"""

from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import List


class ProjectRole(str, Enum):
    """Project access roles"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectPermissionCreate(BaseModel):
    """Create project permission"""
    user_id: str
    role: ProjectRole = ProjectRole.VIEWER


class ProjectPermissionUpdate(BaseModel):
    """Update project permission"""
    role: ProjectRole


class ProjectPermissionResponse(BaseModel):
    """Project permission response"""
    id: str
    project_id: str
    user_id: str
    username: str
    email: str
    role: ProjectRole
    granted_by: str
    granted_at: datetime

    class Config:
        from_attributes = True


class ProjectShareRequest(BaseModel):
    """Share project with users"""
    user_ids: List[str]
    role: ProjectRole = ProjectRole.VIEWER
