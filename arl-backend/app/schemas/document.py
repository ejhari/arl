"""Document schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, List


class DocumentBase(BaseModel):
    """Base document schema"""
    title: str
    metadata: Optional[dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    project_id: str


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: str
    project_id: str
    title: str
    file_name: str
    file_type: str
    file_size: int
    is_processed: bool
    page_count: Optional[int] = None
    uploaded_by: str
    created_at: datetime
    updated_at: datetime
    # Map doc_metadata column to metadata field in response
    metadata: Optional[dict[str, Any]] = Field(default=None, validation_alias="doc_metadata")

    class Config:
        from_attributes = True
        populate_by_name = True


class AnnotationBase(BaseModel):
    """Base annotation schema"""
    annotation_type: str  # highlight, comment, note
    page_number: int
    content: Optional[str] = None
    position: Optional[dict[str, Any]] = None
    color: Optional[str] = None


class AnnotationCreate(AnnotationBase):
    """Annotation creation schema"""
    document_id: str


class AnnotationUpdate(BaseModel):
    """Annotation update schema"""
    content: Optional[str] = None
    position: Optional[dict[str, Any]] = None
    color: Optional[str] = None


class AnnotationResponse(AnnotationBase):
    """Annotation response schema"""
    id: str
    document_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CitationBase(BaseModel):
    """Base citation schema"""
    citation_text: str
    authors: Optional[List[str]] = None
    title: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    page_number: Optional[int] = None


class CitationCreate(CitationBase):
    """Citation creation schema"""
    document_id: str


class CitationResponse(CitationBase):
    """Citation response schema"""
    id: str
    document_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithAnnotations(DocumentResponse):
    """Document with annotations"""
    annotations: List[AnnotationResponse] = []

    class Config:
        from_attributes = True


class DocumentWithCitations(DocumentResponse):
    """Document with citations"""
    citations: List[CitationResponse] = []

    class Config:
        from_attributes = True
