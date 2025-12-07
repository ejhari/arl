"""Add agents and sessions tables

Revision ID: deae3535b65d
Revises: 27757269535a
Create Date: 2025-12-06 19:12:47.031123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'deae3535b65d'
down_revision: Union[str, None] = '27757269535a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agents table
    op.create_table('agents',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('agent_type', sa.String(length=50), nullable=False),
    sa.Column('agent_card', sa.JSON(), nullable=True),
    sa.Column('version', sa.String(length=50), nullable=True),
    sa.Column('service_endpoint', sa.String(length=500), nullable=True),
    sa.Column('protocol_version', sa.String(length=50), nullable=True),
    sa.Column('owner_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('team_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_system', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )

    # Create project_agents table
    op.create_table('project_agents',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('agent_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.Column('agent_config', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create project_memories table
    op.create_table('project_memories',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('memory_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('memory_metadata', sa.JSON(), nullable=True),
    sa.Column('source_session_ids', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create sessions table
    op.create_table('sessions',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('initial_prompt', sa.Text(), nullable=True),
    sa.Column('session_metadata', sa.JSON(), nullable=True),
    sa.Column('created_by', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('archived_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create session_cells table
    op.create_table('session_cells',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('session_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('cell_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('created_by_agent', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create session_memories table
    op.create_table('session_memories',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('session_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('memory_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('memory_metadata', sa.JSON(), nullable=True),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('parent_memory_id', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['parent_memory_id'], ['session_memories.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('session_memories')
    op.drop_table('session_cells')
    op.drop_table('sessions')
    op.drop_table('project_memories')
    op.drop_table('project_agents')
    op.drop_table('agents')
