"""Export endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.export import Export, ExportStatus
from app.models.cell import Cell
from app.schemas.export import ExportCreate, ExportResponse
from app.services.export_service import export_service

router = APIRouter()


@router.post("", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    export_data: ExportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new export job"""
    # Verify project exists and user has access
    result = await db.execute(
        select(Project).where(Project.id == export_data.project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check access (owner or has permission)
    if project.owner_id != current_user.id and not project.is_public:
        # In a full implementation, check project permissions here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Create export record
    export = Export(
        project_id=export_data.project_id,
        created_by=current_user.id,
        format=export_data.format,
        status=ExportStatus.PENDING,
        config={
            "include_code": export_data.include_code,
            "include_outputs": export_data.include_outputs,
            "include_visualizations": export_data.include_visualizations,
        },
    )

    db.add(export)
    await db.commit()
    await db.refresh(export)

    # Start export generation in background (simplified - would use ARQ in production)
    try:
        export.status = ExportStatus.PROCESSING
        await db.commit()

        # Get project cells
        result = await db.execute(
            select(Cell)
            .where(Cell.project_id == export_data.project_id)
            .order_by(Cell.position)
        )
        cells = result.scalars().all()

        # Generate export
        file_path = await export_service.generate_export(export, cells)

        # Update export record
        export.status = ExportStatus.COMPLETED
        export.file_path = file_path
        export.completed_at = datetime.utcnow()

    except Exception as e:
        export.status = ExportStatus.FAILED
        export.error = str(e)

    await db.commit()
    await db.refresh(export)

    return _build_export_response(export)


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get export status"""
    result = await db.execute(
        select(Export).where(Export.id == export_id)
    )
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    # Check access
    if export.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return _build_export_response(export)


@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download export file"""
    result = await db.execute(
        select(Export).where(Export.id == export_id)
    )
    export = result.scalar_one_or_none()

    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found",
        )

    # Check access
    if export.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Check if export is completed
    if export.status != ExportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export is {export.status.value}",
        )

    # Check if file exists
    if not export.file_path or not os.path.exists(export.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found",
        )

    # Determine media type
    media_types = {
        "json": "application/json",
        "markdown": "text/markdown",
        "html": "text/html",
        "pdf": "application/pdf",
    }
    media_type = media_types.get(export.format.value, "application/octet-stream")

    # Get filename
    filename = f"export_{export.project_id}.{export.format.value}"

    return FileResponse(
        path=export.file_path,
        media_type=media_type,
        filename=filename,
    )


@router.get("", response_model=List[ExportResponse])
async def list_exports(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List exports for a project"""
    # Verify project access
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check access
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Get exports
    result = await db.execute(
        select(Export)
        .where(Export.project_id == project_id)
        .order_by(Export.created_at.desc())
    )
    exports = result.scalars().all()

    return [_build_export_response(export) for export in exports]


def _build_export_response(export: Export) -> ExportResponse:
    """Build export response with download URL"""
    download_url = None
    if export.status == ExportStatus.COMPLETED and export.file_path:
        download_url = f"/api/v1/exports/{export.id}/download"

    return ExportResponse(
        id=export.id,
        project_id=export.project_id,
        format=export.format,
        status=export.status,
        created_at=export.created_at,
        completed_at=export.completed_at,
        download_url=download_url,
        error=export.error,
    )
