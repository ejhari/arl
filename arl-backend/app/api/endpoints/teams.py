"""Team management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.team import Team, TeamMember, TeamRole
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamWithMembers,
    TeamMemberAdd,
    TeamMemberUpdate,
    TeamMemberResponse,
)

router = APIRouter()


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all teams where user is a member"""
    # Get teams where user is owner
    result = await db.execute(
        select(Team).where(Team.owner_id == current_user.id)
    )
    owned_teams = result.scalars().all()

    # Get teams where user is a member
    result = await db.execute(
        select(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == current_user.id)
    )
    member_teams = result.scalars().all()

    # Combine and deduplicate
    all_teams = list({team.id: team for team in owned_teams + member_teams}.values())

    return [TeamResponse.model_validate(team) for team in all_teams]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new team"""
    team = Team(
        name=team_data.name,
        description=team_data.description,
        owner_id=current_user.id,
    )

    db.add(team)
    await db.commit()
    await db.refresh(team)

    # Add owner as admin member
    member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role=TeamRole.OWNER,
    )
    db.add(member)
    await db.commit()

    # Return with member_count = 1 (owner is the first member)
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        owner_id=str(team.owner_id),
        created_at=team.created_at,
        updated_at=team.updated_at,
        member_count=1
    )


@router.get("/{team_id}", response_model=TeamWithMembers)
async def get_team(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get team details with members"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check if user has access
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()

    if not membership and team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Get members
    result = await db.execute(
        select(TeamMember, User)
        .join(User, TeamMember.user_id == User.id)
        .where(TeamMember.team_id == team_id)
    )
    members_data = result.all()

    members = [
        TeamMemberResponse(
            user_id=member.user_id,
            username=user.username,
            email=user.email,
            role=member.role,
            joined_at=member.joined_at,
        )
        for member, user in members_data
    ]

    team_dict = TeamResponse.model_validate(team).model_dump()
    team_dict['members'] = members

    return TeamWithMembers(**team_dict)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update team details"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Only owner or admin can update
    if team.owner_id != current_user.id:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership or membership.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner or admin can update team",
            )

    # Update fields
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description

    await db.commit()
    await db.refresh(team)

    return TeamResponse.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete team (owner only)"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team owner can delete team",
        )

    await db.delete(team)
    await db.commit()


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add member to team"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check if current user can add members (owner or admin)
    if team.owner_id != current_user.id:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership or membership.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner or admin can add members",
            )

    # Check if user exists
    result = await db.execute(select(User).where(User.id == member_data.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already a member
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == member_data.user_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member",
        )

    # Add member
    member = TeamMember(
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role,
    )

    db.add(member)
    await db.commit()

    return TeamMemberResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_id: str,
    user_id: str,
    member_data: TeamMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update team member role"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check permissions
    if team.owner_id != current_user.id:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership or membership.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner or admin can update members",
            )

    # Get member
    result = await db.execute(
        select(TeamMember, User)
        .join(User, TeamMember.user_id == User.id)
        .where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )
    member_data_result = result.one_or_none()

    if not member_data_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )

    member, user = member_data_result

    # Update role
    member.role = member_data.role
    await db.commit()

    return TeamMemberResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=member.role,
        joined_at=member.joined_at,
    )


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove member from team"""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Check permissions (owner/admin or self)
    can_remove = False
    if team.owner_id == current_user.id:
        can_remove = True
    elif user_id == current_user.id:
        can_remove = True  # Can remove self
    else:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if membership and membership.role in [TeamRole.OWNER, TeamRole.ADMIN]:
            can_remove = True

    if not can_remove:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Get member
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found",
        )

    # Cannot remove team owner
    if user_id == team.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove team owner",
        )

    await db.delete(member)
    await db.commit()
