"""Event schemas for real-time messaging"""

from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Event types for real-time messaging"""
    # System events
    SYSTEM_MESSAGE = "system_message"
    SYSTEM_NOTIFICATION = "system_notification"

    # User events
    USER_STATUS_CHANGED = "user_status_changed"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"

    # Research events
    RESEARCH_STARTED = "research_started"
    RESEARCH_PROGRESS = "research_progress"
    RESEARCH_COMPLETED = "research_completed"
    RESEARCH_ERROR = "research_error"

    # Agent events
    AGENT_STATUS_CHANGED = "agent_status_changed"
    AGENT_OUTPUT = "agent_output"
    AGENT_ERROR = "agent_error"

    # Cell events
    CELL_CREATED = "cell_created"
    CELL_UPDATED = "cell_updated"
    CELL_DELETED = "cell_deleted"
    CELL_EXECUTED = "cell_executed"


class EventBase(BaseModel):
    """Base event schema"""
    type: EventType
    data: dict[str, Any]
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


class SystemEvent(EventBase):
    """System-level event"""
    type: EventType = EventType.SYSTEM_MESSAGE
    severity: Optional[str] = "info"  # info, warning, error


class UserEvent(EventBase):
    """User-related event"""
    type: EventType
    username: Optional[str] = None


class ResearchEvent(EventBase):
    """Research-related event"""
    type: EventType
    research_id: str
    project_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None


class AgentEvent(EventBase):
    """Agent-related event"""
    type: EventType
    agent_id: str
    agent_type: Optional[str] = None
    status: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None


class CellEvent(EventBase):
    """Cell-related event"""
    type: EventType
    cell_id: str
    project_id: str
    action: str  # created, updated, deleted, executed
    cell_data: Optional[dict] = None


class BroadcastEvent(BaseModel):
    """Event to broadcast to multiple users/rooms"""
    event_type: str
    data: dict[str, Any]
    target_type: str  # "user", "room", "broadcast"
    target_ids: Optional[list[str]] = None  # user_ids or room names
