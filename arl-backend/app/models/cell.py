"""Cell model"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Cell(Base):
    """Cell model - basic unit of content in a project"""

    __tablename__ = "cells"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)
    cell_type = Column(String(50), nullable=False)  # code, markdown, research, visualization
    content = Column(Text, nullable=True)
    cell_metadata = Column(JSON, nullable=True)  # Cell-specific metadata
    position = Column(Integer, nullable=False, default=0)  # Order in project
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="cells")
    outputs = relationship("CellOutput", back_populates="cell", cascade="all, delete-orphan")


class CellOutput(Base):
    """Cell output model - stores execution results"""

    __tablename__ = "cell_outputs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    cell_id = Column(UUID(as_uuid=False), ForeignKey("cells.id"), nullable=False)
    output_type = Column(String(50), nullable=False)  # stdout, stderr, result, error, image
    content = Column(Text, nullable=True)
    output_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    cell = relationship("Cell", back_populates="outputs")
