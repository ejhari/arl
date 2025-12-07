"""Session management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.session import Session, SessionMemory, SessionCell, SessionAgent, ProjectMemory
from app.models.agent import Agent, ProjectAgent
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionWithDetails,
    SessionMemoryCreate,
    SessionMemoryResponse,
    ProjectMemoryResponse,
    ArchiveSessionRequest,
    SessionAgentResponse,
    SessionAgentWithDetails,
)

router = APIRouter()


# Session CRUD endpoints
@router.get("/projects/{project_id}/sessions", response_model=List[SessionResponse])
async def list_sessions(
    project_id: str,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sessions for a project"""
    query = select(Session).where(Session.project_id == project_id)

    if status_filter:
        query = query.where(Session.status == status_filter)

    query = query.order_by(Session.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    # Get counts for each session
    session_responses = []
    for session in sessions:
        # Count memories
        memory_result = await db.execute(
            select(func.count(SessionMemory.id)).where(SessionMemory.session_id == session.id)
        )
        memory_count = memory_result.scalar() or 0

        # Count cells
        cell_result = await db.execute(
            select(func.count(SessionCell.id)).where(SessionCell.session_id == session.id)
        )
        cell_count = cell_result.scalar() or 0

        session_dict = SessionResponse.model_validate(session).model_dump()
        session_dict['memory_count'] = memory_count
        session_dict['cell_count'] = cell_count
        session_responses.append(SessionResponse(**session_dict))

    return session_responses


@router.post("/projects/{project_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    project_id: str,
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new session and copy enabled agents from project"""
    session = Session(
        project_id=project_id,
        name=session_data.name,
        description=session_data.description,
        initial_prompt=session_data.initial_prompt,
        status="active",
        created_by=current_user.id,
    )

    db.add(session)
    await db.flush()  # Get session ID without committing

    # Get all enabled project agents
    project_agents_result = await db.execute(
        select(ProjectAgent).where(
            ProjectAgent.project_id == project_id,
            ProjectAgent.is_enabled == True
        )
    )
    project_agents = project_agents_result.scalars().all()

    # Get all active system agents (always enabled for all sessions)
    system_agents_result = await db.execute(
        select(Agent).where(
            Agent.is_system == True,
            Agent.is_active == True
        )
    )
    system_agents = system_agents_result.scalars().all()

    # Copy project agents to session
    for pa in project_agents:
        session_agent = SessionAgent(
            session_id=session.id,
            agent_id=pa.agent_id,
            is_enabled=pa.is_enabled,
            agent_config=pa.agent_config,
        )
        db.add(session_agent)

    # Add system agents to session (if not already added via project agents)
    added_agent_ids = {pa.agent_id for pa in project_agents}
    for agent in system_agents:
        if agent.id not in added_agent_ids:
            session_agent = SessionAgent(
                session_id=session.id,
                agent_id=agent.id,
                is_enabled=True,
                agent_config=None,
            )
            db.add(session_agent)

    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)


@router.get("/projects/{project_id}/sessions/{session_id}", response_model=SessionWithDetails)
async def get_session(
    project_id: str,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get session details with memories and cells"""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.project_id == project_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get memories
    memory_result = await db.execute(
        select(SessionMemory)
        .where(SessionMemory.session_id == session_id)
        .order_by(SessionMemory.created_at.asc())
    )
    memories = memory_result.scalars().all()

    # Get cells
    cell_result = await db.execute(
        select(SessionCell)
        .where(SessionCell.session_id == session_id)
        .order_by(SessionCell.position.asc())
    )
    cells = cell_result.scalars().all()

    session_dict = SessionResponse.model_validate(session).model_dump()
    session_dict['memories'] = [SessionMemoryResponse.model_validate(m) for m in memories]
    session_dict['cells'] = cells
    session_dict['memory_count'] = len(memories)
    session_dict['cell_count'] = len(cells)

    return SessionWithDetails(**session_dict)


@router.patch("/projects/{project_id}/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    project_id: str,
    session_id: str,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update session details"""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.project_id == project_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'status' and value:
            setattr(session, field, value.value if hasattr(value, 'value') else value)
        else:
            setattr(session, field, value)

    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)


@router.post("/projects/{project_id}/sessions/{session_id}/archive", response_model=SessionResponse)
async def archive_session(
    project_id: str,
    session_id: str,
    archive_data: ArchiveSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Archive a session and create project-level memory"""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.project_id == project_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already archived",
        )

    # Get all session memories for archiving
    memory_result = await db.execute(
        select(SessionMemory).where(SessionMemory.session_id == session_id)
    )
    memories = memory_result.scalars().all()

    # Mark memories as archived
    for memory in memories:
        memory.is_archived = True

    # Create project memory from session if requested
    if archive_data.generate_summary:
        # Compile content from memories
        content_parts = [m.content for m in memories if m.content]
        combined_content = "\n\n".join(content_parts)

        # Create summary (in production, this would use AI)
        summary = f"Archived session: {session.name}. Contains {len(memories)} memories."

        project_memory = ProjectMemory(
            project_id=project_id,
            memory_type="session_archive",
            content=combined_content[:10000] if combined_content else "",
            summary=summary,
            memory_metadata={
                "session_name": session.name,
                "memory_count": len(memories),
                "archived_at": datetime.utcnow().isoformat(),
            },
            source_session_ids=[session_id],
        )
        db.add(project_memory)

    # Update session status
    session.status = "archived"
    session.archived_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)


@router.delete("/projects/{project_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    project_id: str,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a session"""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.project_id == project_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Only creator can delete
    if session.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only session creator can delete session",
        )

    await db.delete(session)
    await db.commit()


# Session Agent endpoints
@router.get("/sessions/{session_id}/agents", response_model=List[SessionAgentWithDetails])
async def list_session_agents(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List agents enabled for a session"""
    # Verify session exists
    session_result = await db.execute(select(Session).where(Session.id == session_id))
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get session agents with agent details
    result = await db.execute(
        select(SessionAgent, Agent)
        .join(Agent, SessionAgent.agent_id == Agent.id)
        .where(SessionAgent.session_id == session_id)
        .order_by(Agent.is_system.desc(), Agent.display_name.asc())
    )
    rows = result.all()

    session_agents = []
    for sa, agent in rows:
        session_agents.append(SessionAgentWithDetails(
            id=sa.id,
            session_id=sa.session_id,
            agent_id=sa.agent_id,
            is_enabled=sa.is_enabled,
            agent_config=sa.agent_config,
            created_at=sa.created_at,
            agent_name=agent.name,
            agent_display_name=agent.display_name,
            agent_description=agent.description,
            is_system=agent.is_system,
        ))

    return session_agents


# Session Memory endpoints
@router.get("/sessions/{session_id}/memories", response_model=List[SessionMemoryResponse])
async def list_session_memories(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List memories for a session"""
    result = await db.execute(
        select(SessionMemory)
        .where(SessionMemory.session_id == session_id)
        .order_by(SessionMemory.created_at.asc())
    )
    memories = result.scalars().all()

    return [SessionMemoryResponse.model_validate(m) for m in memories]


@router.post("/sessions/{session_id}/memories", response_model=SessionMemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_session_memory(
    session_id: str,
    memory_data: SessionMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a memory in a session"""
    # Get session to get project_id
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status == "archived":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add memories to archived session",
        )

    memory = SessionMemory(
        session_id=session_id,
        project_id=session.project_id,
        memory_type=memory_data.memory_type.value if hasattr(memory_data.memory_type, 'value') else memory_data.memory_type,
        content=memory_data.content,
        memory_metadata=memory_data.memory_metadata,
        parent_memory_id=memory_data.parent_memory_id,
    )

    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    return SessionMemoryResponse.model_validate(memory)


# Project Memory endpoints
@router.get("/projects/{project_id}/memories", response_model=List[ProjectMemoryResponse])
async def list_project_memories(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List long-term memories for a project"""
    result = await db.execute(
        select(ProjectMemory)
        .where(ProjectMemory.project_id == project_id)
        .order_by(ProjectMemory.created_at.desc())
    )
    memories = result.scalars().all()

    return [ProjectMemoryResponse.model_validate(m) for m in memories]
