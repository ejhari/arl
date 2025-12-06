"""fix_team_members_schema

Revision ID: 27757269535a
Revises: 7b54b4275a31
Create Date: 2025-12-06 16:51:11.576809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27757269535a'
down_revision: Union[str, None] = '7b54b4275a31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create TeamRole enum type
    op.execute("CREATE TYPE teamrole AS ENUM ('owner', 'admin', 'member', 'viewer')")

    # Drop the id column and make team_id, user_id the composite primary key
    op.drop_constraint('team_members_pkey', 'team_members', type_='primary')
    op.drop_column('team_members', 'id')
    op.create_primary_key('team_members_pkey', 'team_members', ['team_id', 'user_id'])

    # Convert role column to use the enum
    op.execute("ALTER TABLE team_members ALTER COLUMN role TYPE teamrole USING role::teamrole")


def downgrade() -> None:
    # Convert role back to string
    op.execute("ALTER TABLE team_members ALTER COLUMN role TYPE VARCHAR(50) USING role::text")

    # Restore id column and primary key
    op.drop_constraint('team_members_pkey', 'team_members', type_='primary')
    op.add_column('team_members', sa.Column('id', sa.UUID(), nullable=False))
    op.create_primary_key('team_members_pkey', 'team_members', ['id'])

    # Drop TeamRole enum type
    op.execute("DROP TYPE teamrole")
