"""Add session_agents table

Revision ID: a1b2c3d4e5f6
Revises: deae3535b65d
Create Date: 2025-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'deae3535b65d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create session_agents table
    op.create_table('session_agents',
    sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('session_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('agent_id', sa.UUID(as_uuid=False), nullable=False),
    sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
    sa.Column('agent_config', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create index for efficient lookups
    op.create_index('ix_session_agents_session_id', 'session_agents', ['session_id'])
    op.create_index('ix_session_agents_agent_id', 'session_agents', ['agent_id'])


def downgrade() -> None:
    op.drop_index('ix_session_agents_agent_id', 'session_agents')
    op.drop_index('ix_session_agents_session_id', 'session_agents')
    op.drop_table('session_agents')
