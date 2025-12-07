"""Agent management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent, ProjectAgent
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    ProjectAgentCreate,
    ProjectAgentUpdate,
    ProjectAgentResponse,
)

router = APIRouter()


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all agents (system + user's custom agents)"""
    # Get system agents
    result = await db.execute(
        select(Agent).where(Agent.is_system == True)
    )
    system_agents = result.scalars().all()

    # Get user's custom agents
    result = await db.execute(
        select(Agent).where(
            Agent.is_system == False,
            Agent.owner_id == current_user.id,
        )
    )
    custom_agents = result.scalars().all()

    all_agents = list(system_agents) + list(custom_agents)
    return [AgentResponse.model_validate(agent) for agent in all_agents[skip:skip+limit]]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom agent"""
    # Check if agent name already exists
    result = await db.execute(
        select(Agent).where(Agent.name == agent_data.name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists",
        )

    agent = Agent(
        name=agent_data.name,
        display_name=agent_data.display_name,
        description=agent_data.description,
        agent_type="custom",
        agent_card=agent_data.agent_card,
        version=agent_data.version,
        service_endpoint=agent_data.service_endpoint,
        protocol_version=agent_data.protocol_version,
        owner_id=current_user.id,
        team_id=agent_data.team_id,
        is_system=False,
        is_active=True,
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get agent details"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Check access (system agents are public, custom agents require ownership)
    if not agent.is_system and agent.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}/card")
async def get_agent_card(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get A2A agent card (public endpoint)"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent.agent_card or {
        "name": agent.name,
        "description": agent.description,
        "version": agent.version,
        "protocolVersion": agent.protocol_version,
    }


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update custom agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # Only owner can update custom agents
    if agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system agents",
        )

    if agent.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agent owner can update agent",
        )

    # Update fields
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete custom agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if agent.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system agents",
        )

    if agent.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agent owner can delete agent",
        )

    await db.delete(agent)
    await db.commit()


# Project-Agent configuration endpoints
@router.get("/projects/{project_id}/agents", response_model=List[ProjectAgentResponse])
async def list_project_agents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List agent configurations for a project"""
    result = await db.execute(
        select(ProjectAgent, Agent)
        .join(Agent, ProjectAgent.agent_id == Agent.id)
        .where(ProjectAgent.project_id == project_id)
    )
    project_agents_data = result.all()

    return [
        ProjectAgentResponse(
            id=str(pa.id),
            project_id=str(pa.project_id),
            agent_id=str(pa.agent_id),
            is_enabled=pa.is_enabled,
            agent_config=pa.agent_config,
            created_at=pa.created_at,
            updated_at=pa.updated_at,
            agent=AgentResponse.model_validate(agent),
        )
        for pa, agent in project_agents_data
    ]


@router.post("/projects/{project_id}/agents/{agent_id}", response_model=ProjectAgentResponse, status_code=status.HTTP_201_CREATED)
async def enable_agent_for_project(
    project_id: str,
    agent_id: str,
    config_data: ProjectAgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable an agent for a project"""
    # Check if already configured
    result = await db.execute(
        select(ProjectAgent).where(
            ProjectAgent.project_id == project_id,
            ProjectAgent.agent_id == agent_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is already configured for this project",
        )

    # Verify agent exists
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    project_agent = ProjectAgent(
        project_id=project_id,
        agent_id=agent_id,
        is_enabled=config_data.is_enabled,
        agent_config=config_data.agent_config,
    )

    db.add(project_agent)
    await db.commit()
    await db.refresh(project_agent)

    return ProjectAgentResponse(
        id=str(project_agent.id),
        project_id=str(project_agent.project_id),
        agent_id=str(project_agent.agent_id),
        is_enabled=project_agent.is_enabled,
        agent_config=project_agent.agent_config,
        created_at=project_agent.created_at,
        updated_at=project_agent.updated_at,
        agent=AgentResponse.model_validate(agent),
    )


@router.patch("/projects/{project_id}/agents/{agent_id}", response_model=ProjectAgentResponse)
async def update_project_agent(
    project_id: str,
    agent_id: str,
    config_data: ProjectAgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update agent configuration for a project"""
    result = await db.execute(
        select(ProjectAgent, Agent)
        .join(Agent, ProjectAgent.agent_id == Agent.id)
        .where(
            ProjectAgent.project_id == project_id,
            ProjectAgent.agent_id == agent_id,
        )
    )
    data = result.one_or_none()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project agent configuration not found",
        )

    project_agent, agent = data

    # Update fields
    if config_data.is_enabled is not None:
        project_agent.is_enabled = config_data.is_enabled
    if config_data.agent_config is not None:
        project_agent.agent_config = config_data.agent_config

    await db.commit()
    await db.refresh(project_agent)

    return ProjectAgentResponse(
        id=str(project_agent.id),
        project_id=str(project_agent.project_id),
        agent_id=str(project_agent.agent_id),
        is_enabled=project_agent.is_enabled,
        agent_config=project_agent.agent_config,
        created_at=project_agent.created_at,
        updated_at=project_agent.updated_at,
        agent=AgentResponse.model_validate(agent),
    )


@router.delete("/projects/{project_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_agent_for_project(
    project_id: str,
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disable/remove an agent from a project"""
    result = await db.execute(
        select(ProjectAgent).where(
            ProjectAgent.project_id == project_id,
            ProjectAgent.agent_id == agent_id,
        )
    )
    project_agent = result.scalar_one_or_none()

    if not project_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project agent configuration not found",
        )

    await db.delete(project_agent)
    await db.commit()
