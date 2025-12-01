"""Project schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectWithCells(ProjectResponse):
    """Project with cells included"""
    cells: list["CellResponse"] = []

    class Config:
        from_attributes = True


# Forward reference for CellResponse
from app.schemas.cell import CellResponse
ProjectWithCells.model_rebuild()
