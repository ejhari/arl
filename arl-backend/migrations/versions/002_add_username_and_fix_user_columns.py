"""Add username and fix user columns

Revision ID: 002_fix_user_schema
Revises: 001_initial_schema
Create Date: 2025-12-02 00:50:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_fix_user_schema'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add username column (nullable first, then make it required)
    op.add_column('users', sa.Column('username', sa.String(length=100), nullable=True))

    # Add updated_at column with default value
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # Rename hashed_password to password_hash
    op.alter_column('users', 'hashed_password', new_column_name='password_hash')

    # Rename is_superuser to is_admin
    op.alter_column('users', 'is_superuser', new_column_name='is_admin')

    # Create unique constraint and index on username
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Make username non-nullable (should be done after populating existing rows if any)
    # For now, we'll keep it nullable since there might be existing users


def downgrade() -> None:
    # Drop index and constraint
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_constraint('uq_users_username', 'users', type_='unique')

    # Rename columns back
    op.alter_column('users', 'is_admin', new_column_name='is_superuser')
    op.alter_column('users', 'password_hash', new_column_name='hashed_password')

    # Drop added columns
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'username')
