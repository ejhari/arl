"""Team schemas for request/response validation"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TeamRole(str, Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamMemberResponse(BaseModel):
    """Team member response"""
    user_id: str
    username: str
    email: str
    role: TeamRole
    joined_at: datetime

    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    """Base team schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class TeamCreate(TeamBase):
    """Team creation schema"""
    pass


class TeamUpdate(BaseModel):
    """Team update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class TeamResponse(TeamBase):
    """Team response schema"""
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TeamWithMembers(TeamResponse):
    """Team with members list"""
    members: List[TeamMemberResponse] = []


class TeamMemberAdd(BaseModel):
    """Add team member schema"""
    user_id: str
    role: TeamRole = TeamRole.MEMBER


class TeamMemberUpdate(BaseModel):
    """Update team member role"""
    role: TeamRole
