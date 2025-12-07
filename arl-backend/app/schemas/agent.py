"""Agent schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class AgentType(str, Enum):
    """Agent type enum"""
    SYSTEM = "system"
    CUSTOM = "custom"


# A2A Protocol schemas
class AgentSkill(BaseModel):
    """A2A Agent skill definition"""
    id: str
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    inputModes: Optional[List[str]] = None
    outputModes: Optional[List[str]] = None


class AgentCapabilities(BaseModel):
    """A2A Agent capabilities"""
    streaming: Optional[bool] = False
    pushNotifications: Optional[bool] = False
    stateTransitionHistory: Optional[bool] = False


class AgentAuthentication(BaseModel):
    """A2A Agent authentication"""
    schemes: Optional[List[str]] = None


class AgentCard(BaseModel):
    """A2A Protocol Agent Card specification"""
    name: str
    description: str
    url: Optional[str] = None
    version: Optional[str] = "1.0.0"
    protocolVersion: Optional[str] = "0.3"
    capabilities: Optional[AgentCapabilities] = None
    skills: Optional[List[AgentSkill]] = None
    authentication: Optional[AgentAuthentication] = None
    defaultInputModes: Optional[List[str]] = None
    defaultOutputModes: Optional[List[str]] = None


# Agent CRUD schemas
class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class AgentCreate(AgentBase):
    """Agent creation schema"""
    agent_card: Optional[Dict[str, Any]] = None
    version: Optional[str] = "1.0.0"
    service_endpoint: Optional[str] = None
    protocol_version: Optional[str] = "0.3"
    team_id: Optional[str] = None


class AgentUpdate(BaseModel):
    """Agent update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agent_card: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    service_endpoint: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """Agent response schema"""
    id: str
    agent_type: str
    agent_card: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    service_endpoint: Optional[str] = None
    protocol_version: Optional[str] = None
    owner_id: Optional[str] = None
    team_id: Optional[str] = None
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project-Agent configuration schemas
class ProjectAgentBase(BaseModel):
    """Base project-agent config schema"""
    is_enabled: bool = True
    agent_config: Optional[Dict[str, Any]] = None


class ProjectAgentCreate(ProjectAgentBase):
    """Create project-agent config"""
    agent_id: str


class ProjectAgentUpdate(BaseModel):
    """Update project-agent config"""
    is_enabled: Optional[bool] = None
    agent_config: Optional[Dict[str, Any]] = None


class ProjectAgentResponse(ProjectAgentBase):
    """Project-agent config response"""
    id: str
    project_id: str
    agent_id: str
    created_at: datetime
    updated_at: datetime
    agent: Optional[AgentResponse] = None

    class Config:
        from_attributes = True
