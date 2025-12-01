"""SQLAlchemy models for ARL entities."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from arl.storage.database import Base


class DomainType(str, Enum):
    """Scientific domain types."""

    CS = "cs"
    BIOLOGY = "biology"
    PHYSICS = "physics"
    GENERAL = "general"


class SessionStatus(str, Enum):
    """Session lifecycle states."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ExperimentStatus(str, Enum):
    """Experiment execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PaperSource(str, Enum):
    """Paper ingestion sources."""

    ARXIV = "arxiv"
    PUBMED = "pubmed"
    SCHOLAR = "scholar"
    MANUAL = "manual"


def generate_uuid() -> str:
    """Generate UUID string."""
    return str(uuid.uuid4())


class Project(Base):
    """Research project container."""

    __tablename__ = "projects"

    project_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    domain = Column(SQLEnum(DomainType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    objectives = Column(Text, nullable=True)
    constraints = Column(JSON, nullable=True)
    memory_id = Column(String(255), nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="project", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="project", cascade="all, delete-orphan")


class Session(Base):
    """Research session within a project."""

    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    state = Column(JSON, nullable=True)  # ADK session state
    events = Column(JSON, nullable=True)  # Event log
    checkpoints = Column(JSON, nullable=True)  # Saved checkpoints

    # Relationships
    project = relationship("Project", back_populates="sessions")
    experiments = relationship("Experiment", back_populates="session", cascade="all, delete-orphan")


class Paper(Base):
    """Academic paper in library."""

    __tablename__ = "papers"

    paper_id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, nullable=True)  # List of author names
    publication = Column(String(255), nullable=True)
    year = Column(String(4), nullable=True)
    doi = Column(String(255), nullable=True)
    arxiv_id = Column(String(50), nullable=True)
    pubmed_id = Column(String(50), nullable=True)
    source = Column(SQLEnum(PaperSource), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    paper_metadata = Column(JSON, nullable=True)
    extracted_knowledge = Column(JSON, nullable=True)
    citations = Column(JSON, nullable=True)  # List of cited paper IDs

    # Relationships
    project = relationship("Project", back_populates="papers")


class Experiment(Base):
    """Experiment execution record."""

    __tablename__ = "experiments"

    experiment_id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False)
    hypothesis = Column(Text, nullable=False)
    design = Column(JSON, nullable=True)  # Experiment protocol
    code = Column(Text, nullable=True)  # Generated code
    code_version = Column(String(64), nullable=True)  # Git hash or version
    execution_time = Column(DateTime, nullable=True)
    status = Column(SQLEnum(ExperimentStatus), default=ExperimentStatus.PENDING, nullable=False)
    results = Column(JSON, nullable=True)
    artifacts = Column(JSON, nullable=True)  # List of artifact paths
    analysis = Column(JSON, nullable=True)
    lineage = Column(String(36), nullable=True)  # Parent experiment ID

    # Relationships
    session = relationship("Session", back_populates="experiments")
