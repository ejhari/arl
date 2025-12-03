"""Document endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.storage import file_storage
from app.models.user import User
from app.models.project import Project
from app.models.document import Document, Annotation
from app.schemas.document import (
    DocumentResponse,
    DocumentWithAnnotations,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
)

router = APIRouter()


async def check_project_access(project_id: str, user_id: str, db: AsyncSession) -> Project:
    """Check if user has access to project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != user_id and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return project


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document"""
    # Check project access
    await check_project_access(project_id, current_user.id, db)

    # Validate file type
    if file.content_type not in ["application/pdf", "text/plain", "application/msword"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Save file
    file_path = await file_storage.save_file(
        file_content,
        current_user.id,
        project_id,
        file.filename or "document.pdf"
    )

    # Create document record
    document = Document(
        project_id=project_id,
        title=title,
        file_path=file_path,
        file_name=file.filename or "document.pdf",
        file_type=file.content_type or "application/pdf",
        file_size=file_size,
        uploaded_by=current_user.id,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentResponse.model_validate(document)


@router.get("/project/{project_id}", response_model=List[DocumentResponse])
async def list_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List documents in a project"""
    # Check project access
    await check_project_access(project_id, current_user.id, db)

    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return [DocumentResponse.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentWithAnnotations)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get document with annotations"""
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.annotations))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check project access
    await check_project_access(document.project_id, current_user.id, db)

    return DocumentWithAnnotations.model_validate(document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download document file"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check project access
    await check_project_access(document.project_id, current_user.id, db)

    # Read file
    try:
        file_content = await file_storage.read_file(document.file_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )

    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=document.file_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.file_name}"'
        }
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete document"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check project access (must be owner)
    project = await check_project_access(document.project_id, current_user.id, db)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete documents",
        )

    # Delete file
    file_storage.delete_file(document.file_path)

    # Delete document record
    await db.delete(document)
    await db.commit()

    return None


# Annotation endpoints
@router.post("/annotations", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    annotation_data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create annotation"""
    # Verify document exists and user has access
    result = await db.execute(
        select(Document).where(Document.id == annotation_data.document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await check_project_access(document.project_id, current_user.id, db)

    annotation = Annotation(
        document_id=annotation_data.document_id,
        user_id=current_user.id,
        annotation_type=annotation_data.annotation_type,
        page_number=annotation_data.page_number,
        content=annotation_data.content,
        position=annotation_data.position,
        color=annotation_data.color,
    )

    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)

    return AnnotationResponse.model_validate(annotation)


@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete annotation"""
    result = await db.execute(
        select(Annotation).where(Annotation.id == annotation_id)
    )
    annotation = result.scalar_one_or_none()

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annotation not found",
        )

    # Only creator can delete
    if annotation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only annotation creator can delete it",
        )

    await db.delete(annotation)
    await db.commit()

    return None
