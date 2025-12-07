"""Agent models for A2A protocol support"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Agent(Base):
    """Agent model - represents AI agents with A2A protocol support"""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False, default="custom")  # 'system' | 'custom'

    # A2A Protocol fields
    agent_card = Column(JSON, nullable=True)  # Full AgentCard specification
    version = Column(String(50), nullable=True, default="1.0.0")
    service_endpoint = Column(String(500), nullable=True)
    protocol_version = Column(String(50), nullable=True, default="0.3")

    # Ownership (nullable for system agents)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    team = relationship("Team", foreign_keys=[team_id])
    project_agents = relationship("ProjectAgent", back_populates="agent", cascade="all, delete-orphan")


class ProjectAgent(Base):
    """Project-Agent configuration - enables agents per project"""

    __tablename__ = "project_agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False)

    # Configuration
    is_enabled = Column(Boolean, default=True, nullable=False)
    agent_config = Column(JSON, nullable=True)  # Project-specific agent settings

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project")
    agent = relationship("Agent", back_populates="project_agents")

    # Unique constraint on project_id + agent_id
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
