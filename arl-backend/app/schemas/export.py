"""Export schemas for request/response validation"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ExportFormat(str, Enum):
    """Export format types"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class ExportStatus(str, Enum):
    """Export job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportConfig(BaseModel):
    """Export configuration options"""
    include_code: bool = True
    include_outputs: bool = True
    include_visualizations: bool = True


class ExportCreate(BaseModel):
    """Create export request"""
    project_id: str
    format: ExportFormat
    include_code: Optional[bool] = True
    include_outputs: Optional[bool] = True
    include_visualizations: Optional[bool] = True


class ExportResponse(BaseModel):
    """Export response schema"""
    id: str
    project_id: str
    format: ExportFormat
    status: ExportStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True
