"""Cell endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.cell import Cell, CellOutput
from app.schemas.cell import (
    CellCreate,
    CellUpdate,
    CellResponse,
    CellWithOutputs,
    CellExecuteRequest,
    CellExecuteResponse,
)
from app.services.event_service import event_service
from app.schemas.event import EventType

router = APIRouter()


async def check_project_access(project_id: str, user_id: str, db: AsyncSession) -> Project:
    """Check if user has access to project"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
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


@router.post("", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
async def create_cell(
    cell_data: CellCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new cell"""
    # Check project access
    await check_project_access(cell_data.project_id, current_user.id, db)

    cell = Cell(
        project_id=cell_data.project_id,
        cell_type=cell_data.cell_type.value,
        content=cell_data.content,
        cell_metadata=cell_data.metadata or {},
        position=cell_data.position,
        created_by=current_user.id,
    )

    db.add(cell)
    await db.commit()
    await db.refresh(cell)

    # Emit real-time event
    await event_service.emit_cell_event(
        cell_id=cell.id,
        project_id=cell.project_id,
        user_id=current_user.id,
        action="created",
        cell_data={
            "id": cell.id,
            "cell_type": cell.cell_type,
            "position": cell.position,
        }
    )

    return CellResponse.model_validate(cell)


@router.get("/project/{project_id}", response_model=List[CellResponse])
async def list_cells(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List cells in a project"""
    # Check project access
    await check_project_access(project_id, current_user.id, db)

    result = await db.execute(
        select(Cell)
        .where(Cell.project_id == project_id)
        .order_by(Cell.position.asc(), Cell.created_at.asc())
    )
    cells = result.scalars().all()

    return [CellResponse.model_validate(c) for c in cells]


@router.get("/{cell_id}", response_model=CellWithOutputs)
async def get_cell(
    cell_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific cell with outputs"""
    result = await db.execute(
        select(Cell)
        .options(selectinload(Cell.outputs))
        .where(Cell.id == cell_id)
    )
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found",
        )

    # Check project access
    await check_project_access(cell.project_id, current_user.id, db)

    return CellWithOutputs.model_validate(cell)


@router.patch("/{cell_id}", response_model=CellResponse)
async def update_cell(
    cell_id: str,
    cell_data: CellUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a cell"""
    result = await db.execute(
        select(Cell).where(Cell.id == cell_id)
    )
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found",
        )

    # Check project access
    project = await check_project_access(cell.project_id, current_user.id, db)

    # Only owner can edit
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can edit cells",
        )

    # Update fields
    if cell_data.content is not None:
        cell.content = cell_data.content
    if cell_data.metadata is not None:
        cell.cell_metadata = cell_data.metadata
    if cell_data.position is not None:
        cell.position = cell_data.position

    await db.commit()
    await db.refresh(cell)

    # Emit real-time event
    await event_service.emit_cell_event(
        cell_id=cell.id,
        project_id=cell.project_id,
        user_id=current_user.id,
        action="updated",
        cell_data={
            "id": cell.id,
            "content": cell.content,
            "position": cell.position,
        }
    )

    return CellResponse.model_validate(cell)


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cell(
    cell_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a cell"""
    result = await db.execute(
        select(Cell).where(Cell.id == cell_id)
    )
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found",
        )

    # Check project access
    project = await check_project_access(cell.project_id, current_user.id, db)

    # Only owner can delete
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete cells",
        )

    project_id = cell.project_id

    await db.delete(cell)
    await db.commit()

    # Emit real-time event
    await event_service.emit_cell_event(
        cell_id=cell_id,
        project_id=project_id,
        user_id=current_user.id,
        action="deleted",
    )

    return None


@router.post("/execute", response_model=CellExecuteResponse)
async def execute_cell(
    execute_request: CellExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a code cell"""
    from app.services.code_executor import code_executor
    from app.schemas.cell import CellOutputCreate

    result = await db.execute(
        select(Cell).where(Cell.id == execute_request.cell_id)
    )
    cell = result.scalar_one_or_none()

    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found",
        )

    # Check project access
    await check_project_access(cell.project_id, current_user.id, db)

    if cell.cell_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only code cells can be executed",
        )

    if not cell.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cell has no content to execute",
        )

    # Execute code
    execution_result = await code_executor.execute(
        cell.content,
        context=execute_request.context or {}
    )

    # Save outputs to database
    outputs = []

    if execution_result["stdout"]:
        output = CellOutput(
            cell_id=cell.id,
            output_type="stdout",
            content=execution_result["stdout"],
        )
        db.add(output)
        outputs.append(output)

    if execution_result["stderr"]:
        output = CellOutput(
            cell_id=cell.id,
            output_type="stderr",
            content=execution_result["stderr"],
        )
        db.add(output)
        outputs.append(output)

    if execution_result["result"]:
        output = CellOutput(
            cell_id=cell.id,
            output_type="result",
            content=execution_result["result"],
        )
        db.add(output)
        outputs.append(output)

    if execution_result["error"]:
        output = CellOutput(
            cell_id=cell.id,
            output_type="error",
            content=execution_result["error"],
        )
        db.add(output)
        outputs.append(output)

    await db.commit()

    # Refresh outputs
    for output in outputs:
        await db.refresh(output)

    # Emit real-time event
    await event_service.emit_cell_event(
        cell_id=cell.id,
        project_id=cell.project_id,
        user_id=current_user.id,
        action="executed",
        cell_data={
            "status": execution_result["status"],
            "output_count": len(outputs),
        }
    )

    # Convert to response format
    from app.schemas.cell import CellOutputResponse
    output_responses = [CellOutputResponse.model_validate(o) for o in outputs]

    return CellExecuteResponse(
        cell_id=cell.id,
        status=execution_result["status"],
        outputs=output_responses,
        error=execution_result.get("error"),
    )
