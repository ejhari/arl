"""Session models for multi-agent research contexts"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Session(Base):
    """Session model - isolated context for multi-agent interactions"""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Status: 'active' | 'completed' | 'archived' | 'failed'
    status = Column(String(50), nullable=False, default="active")
    initial_prompt = Column(Text, nullable=True)
    session_metadata = Column(JSON, nullable=True)  # Agent activity logs, progress

    # Ownership
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project")
    creator = relationship("User", foreign_keys=[created_by])
    memories = relationship("SessionMemory", back_populates="session", cascade="all, delete-orphan")
    cells = relationship("SessionCell", back_populates="session", cascade="all, delete-orphan")
    session_agents = relationship("SessionAgent", back_populates="session", cascade="all, delete-orphan")


class SessionMemory(Base):
    """Session memory - short-term memories within a session"""

    __tablename__ = "session_memories"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("sessions.id"), nullable=False)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)

    # Memory content
    memory_type = Column(String(50), nullable=False)  # 'conversation' | 'result' | 'artifact'
    content = Column(Text, nullable=False)
    memory_metadata = Column(JSON, nullable=True)  # Agent source, timestamp, importance

    # Hierarchy
    is_archived = Column(Boolean, default=False, nullable=False)
    parent_memory_id = Column(UUID(as_uuid=False), ForeignKey("session_memories.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="memories")
    project = relationship("Project")
    parent = relationship("SessionMemory", remote_side=[id])


class SessionCell(Base):
    """Session cell - links cells to sessions with agent attribution"""

    __tablename__ = "session_cells"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("sessions.id"), nullable=False)
    cell_id = Column(UUID(as_uuid=False), ForeignKey("cells.id"), nullable=False)

    position = Column(Integer, nullable=False, default=0)
    created_by_agent = Column(String(255), nullable=True)  # Agent name that created this cell

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="cells")
    cell = relationship("Cell")


class SessionAgent(Base):
    """Session-Agent association - agents enabled for a specific session"""

    __tablename__ = "session_agents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("sessions.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=False), ForeignKey("agents.id"), nullable=False)

    # Configuration (copied from project agent at session creation)
    is_enabled = Column(Boolean, default=True, nullable=False)
    agent_config = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="session_agents")
    agent = relationship("Agent")


class ProjectMemory(Base):
    """Project memory - long-term memories at project level (from archived sessions)"""

    __tablename__ = "project_memories"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)

    # Memory content
    memory_type = Column(String(50), nullable=False)  # 'session_archive' | 'knowledge' | 'pattern'
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Compacted summary
    memory_metadata = Column(JSON, nullable=True)  # Source sessions, importance, tags
    source_session_ids = Column(JSON, nullable=True)  # Array of session IDs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project")
