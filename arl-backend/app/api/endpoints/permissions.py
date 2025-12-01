"""Project permissions endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.permission import ProjectPermission, ProjectRole
from app.schemas.permission import (
    ProjectPermissionCreate,
    ProjectPermissionUpdate,
    ProjectPermissionResponse,
    ProjectShareRequest,
)

router = APIRouter()


@router.get("/projects/{project_id}/permissions", response_model=List[ProjectPermissionResponse])
async def list_project_permissions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all permissions for a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Only owner can view permissions
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can view permissions",
        )

    result = await db.execute(
        select(ProjectPermission, User)
        .join(User, ProjectPermission.user_id == User.id)
        .where(ProjectPermission.project_id == project_id)
    )
    permissions_data = result.all()

    permissions = [
        ProjectPermissionResponse(
            id=perm.id,
            project_id=perm.project_id,
            user_id=perm.user_id,
            username=user.username,
            email=user.email,
            role=perm.role,
            granted_by=perm.granted_by,
            granted_at=perm.granted_at,
        )
        for perm, user in permissions_data
    ]

    return permissions


@router.post("/projects/{project_id}/permissions", response_model=ProjectPermissionResponse, status_code=status.HTTP_201_CREATED)
async def add_project_permission(
    project_id: str,
    perm_data: ProjectPermissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add permission to project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Only owner can add permissions
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can add permissions",
        )

    # Check if user exists
    result = await db.execute(select(User).where(User.id == perm_data.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if permission already exists
    result = await db.execute(
        select(ProjectPermission).where(
            ProjectPermission.project_id == project_id,
            ProjectPermission.user_id == perm_data.user_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists",
        )

    # Create permission
    permission = ProjectPermission(
        project_id=project_id,
        user_id=perm_data.user_id,
        role=perm_data.role,
        granted_by=current_user.id,
    )

    db.add(permission)
    await db.commit()
    await db.refresh(permission)

    return ProjectPermissionResponse(
        id=permission.id,
        project_id=permission.project_id,
        user_id=permission.user_id,
        username=user.username,
        email=user.email,
        role=permission.role,
        granted_by=permission.granted_by,
        granted_at=permission.granted_at,
    )


@router.post("/projects/{project_id}/share", response_model=List[ProjectPermissionResponse])
async def share_project(
    project_id: str,
    share_data: ProjectShareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Share project with multiple users"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Only owner can share
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can share project",
        )

    created_permissions = []

    for user_id in share_data.user_ids:
        # Check if user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            continue  # Skip non-existent users

        # Check if permission already exists
        result = await db.execute(
            select(ProjectPermission).where(
                ProjectPermission.project_id == project_id,
                ProjectPermission.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            continue  # Skip existing permissions

        # Create permission
        permission = ProjectPermission(
            project_id=project_id,
            user_id=user_id,
            role=share_data.role,
            granted_by=current_user.id,
        )

        db.add(permission)
        await db.flush()
        await db.refresh(permission)

        created_permissions.append(
            ProjectPermissionResponse(
                id=permission.id,
                project_id=permission.project_id,
                user_id=permission.user_id,
                username=user.username,
                email=user.email,
                role=permission.role,
                granted_by=permission.granted_by,
                granted_at=permission.granted_at,
            )
        )

    await db.commit()

    return created_permissions


@router.patch("/permissions/{permission_id}", response_model=ProjectPermissionResponse)
async def update_project_permission(
    permission_id: str,
    perm_data: ProjectPermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update project permission role"""
    result = await db.execute(select(ProjectPermission).where(ProjectPermission.id == permission_id))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    # Check if user owns the project
    result = await db.execute(select(Project).where(Project.id == permission.project_id))
    project = result.scalar_one_or_none()

    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can update permissions",
        )

    # Update role
    permission.role = perm_data.role
    await db.commit()
    await db.refresh(permission)

    # Get user info
    result = await db.execute(select(User).where(User.id == permission.user_id))
    user = result.scalar_one_or_none()

    return ProjectPermissionResponse(
        id=permission.id,
        project_id=permission.project_id,
        user_id=permission.user_id,
        username=user.username if user else "",
        email=user.email if user else "",
        role=permission.role,
        granted_by=permission.granted_by,
        granted_at=permission.granted_at,
    )


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_permission(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove project permission"""
    result = await db.execute(select(ProjectPermission).where(ProjectPermission.id == permission_id))
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    # Check if user owns the project
    result = await db.execute(select(Project).where(Project.id == permission.project_id))
    project = result.scalar_one_or_none()

    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can remove permissions",
        )

    await db.delete(permission)
    await db.commit()
