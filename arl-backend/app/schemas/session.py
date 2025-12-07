"""Session schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class MemoryType(str, Enum):
    """Memory type enum"""
    CONVERSATION = "conversation"
    RESULT = "result"
    ARTIFACT = "artifact"
    INSIGHT = "insight"
    DECISION = "decision"


class ProjectMemoryType(str, Enum):
    """Project memory type enum"""
    SESSION_ARCHIVE = "session_archive"
    KNOWLEDGE = "knowledge"
    PATTERN = "pattern"


# Session CRUD schemas
class SessionBase(BaseModel):
    """Base session schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class SessionCreate(SessionBase):
    """Session creation schema"""
    initial_prompt: Optional[str] = None


class SessionUpdate(BaseModel):
    """Session update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[SessionStatus] = None


class SessionResponse(SessionBase):
    """Session response schema"""
    id: str
    project_id: str
    status: str
    initial_prompt: Optional[str] = None
    session_metadata: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    memory_count: Optional[int] = 0
    cell_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Session Memory schemas
class SessionMemoryBase(BaseModel):
    """Base session memory schema"""
    memory_type: MemoryType
    content: str


class SessionMemoryCreate(SessionMemoryBase):
    """Create session memory"""
    memory_metadata: Optional[Dict[str, Any]] = None
    parent_memory_id: Optional[str] = None


class SessionMemoryResponse(SessionMemoryBase):
    """Session memory response"""
    id: str
    session_id: str
    project_id: str
    memory_metadata: Optional[Dict[str, Any]] = None
    is_archived: bool
    parent_memory_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Session Cell schemas
class SessionCellResponse(BaseModel):
    """Session cell response"""
    id: str
    session_id: str
    cell_id: str
    position: int
    created_by_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Project Memory schemas
class ProjectMemoryBase(BaseModel):
    """Base project memory schema"""
    memory_type: ProjectMemoryType
    content: str
    summary: Optional[str] = None


class ProjectMemoryCreate(ProjectMemoryBase):
    """Create project memory"""
    memory_metadata: Optional[Dict[str, Any]] = None
    source_session_ids: Optional[List[str]] = None


class ProjectMemoryResponse(ProjectMemoryBase):
    """Project memory response"""
    id: str
    project_id: str
    memory_metadata: Optional[Dict[str, Any]] = None
    source_session_ids: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Session with details
class SessionWithDetails(SessionResponse):
    """Session with memories and cells"""
    memories: Optional[List[SessionMemoryResponse]] = []
    cells: Optional[List[SessionCellResponse]] = []


# Archive request
class ArchiveSessionRequest(BaseModel):
    """Archive session request"""
    generate_summary: bool = True


# Session Agent schemas
class SessionAgentResponse(BaseModel):
    """Session agent response"""
    id: str
    session_id: str
    agent_id: str
    is_enabled: bool
    agent_config: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionAgentWithDetails(SessionAgentResponse):
    """Session agent with agent details"""
    agent_name: Optional[str] = None
    agent_display_name: Optional[str] = None
    agent_description: Optional[str] = None
    is_system: Optional[bool] = None
