"""rename_teams_created_by_to_owner_id

Revision ID: 7b54b4275a31
Revises: 002_fix_user_schema
Create Date: 2025-12-06 16:44:03.310157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b54b4275a31'
down_revision: Union[str, None] = '002_fix_user_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename created_by to owner_id in teams table
    op.alter_column('teams', 'created_by', new_column_name='owner_id')
    # Add updated_at column
    op.add_column('teams', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column('teams', 'updated_at')
    # Rename owner_id back to created_by
    op.alter_column('teams', 'owner_id', new_column_name='created_by')
