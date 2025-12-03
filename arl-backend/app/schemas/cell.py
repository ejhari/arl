"""Cell schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class CellType(str, Enum):
    """Cell types"""
    CODE = "code"
    MARKDOWN = "markdown"
    RESEARCH = "research"
    VISUALIZATION = "visualization"


class CellBase(BaseModel):
    """Base cell schema"""
    cell_type: CellType
    content: Optional[str] = None
    metadata: Optional[dict[str, Any]] = Field(default=None, validation_alias="cell_metadata")
    position: int = 0


class CellCreate(CellBase):
    """Cell creation schema"""
    project_id: str


class CellUpdate(BaseModel):
    """Cell update schema"""
    content: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    position: Optional[int] = None


class CellOutputBase(BaseModel):
    """Base cell output schema"""
    output_type: str
    content: Optional[str] = None
    metadata: Optional[dict[str, Any]] = Field(default=None, validation_alias="output_metadata")


class CellOutputCreate(CellOutputBase):
    """Cell output creation schema"""
    cell_id: str


class CellOutputResponse(CellOutputBase):
    """Cell output response schema"""
    id: str
    cell_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CellResponse(CellBase):
    """Cell response schema"""
    id: str
    project_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CellWithOutputs(CellResponse):
    """Cell with outputs included"""
    outputs: list[CellOutputResponse] = []

    class Config:
        from_attributes = True


class CellExecuteRequest(BaseModel):
    """Cell execution request"""
    cell_id: str
    context: Optional[dict[str, Any]] = None


class CellExecuteResponse(BaseModel):
    """Cell execution response"""
    cell_id: str
    status: str  # success, error, running
    outputs: list[CellOutputResponse] = []
    error: Optional[str] = None
