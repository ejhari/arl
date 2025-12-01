"""Document model for research papers and files"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Document(Base):
    """Document model for storing research papers, PDFs, etc."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=False), ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)  # Path to stored file
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, doc, txt, etc.
    file_size = Column(Integer, nullable=False)  # Size in bytes
    doc_metadata = Column(JSON, nullable=True)  # Authors, publication date, DOI, etc.
    is_processed = Column(Boolean, default=False)  # For citation extraction
    page_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Relationships
    annotations = relationship("Annotation", back_populates="document", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="document", cascade="all, delete-orphan")


class Annotation(Base):
    """Annotation model for PDF highlights and notes"""

    __tablename__ = "annotations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    annotation_type = Column(String(50), nullable=False)  # highlight, comment, note
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)  # Comment or note text
    position = Column(JSON, nullable=True)  # x, y, width, height for highlight
    color = Column(String(20), nullable=True)  # Highlight color
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="annotations")


class Citation(Base):
    """Citation model for extracted references"""

    __tablename__ = "citations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False)
    citation_text = Column(Text, nullable=False)
    authors = Column(JSON, nullable=True)  # List of author names
    title = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)
    venue = Column(String(500), nullable=True)  # Journal/Conference name
    doi = Column(String(255), nullable=True)
    url = Column(String(1000), nullable=True)
    page_number = Column(Integer, nullable=True)  # Where it appears in source doc
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="citations")
