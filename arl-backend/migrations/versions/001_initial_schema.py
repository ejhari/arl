"""Initial schema with all tables including exports

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-01 21:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )

    # Create teams table
    op.create_table('teams',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create projects table
    op.create_table('projects',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('owner_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('team_id', postgresql.UUID(as_uuid=False), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create cells table
    op.create_table('cells',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('cell_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('cell_metadata', sa.JSON(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create cell_outputs table
    op.create_table('cell_outputs',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('cell_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('output_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('output_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cell_id'], ['cells.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table('documents',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('file_type', sa.String(length=50), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('doc_metadata', sa.JSON(), nullable=True),
    sa.Column('is_processed', sa.Boolean(), nullable=True, server_default='false'),
    sa.Column('page_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('uploaded_by', postgresql.UUID(as_uuid=False), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create annotations table
    op.create_table('annotations',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('annotation_type', sa.String(length=50), nullable=False),
    sa.Column('page_number', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('position', sa.JSON(), nullable=True),
    sa.Column('color', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create citations table
    op.create_table('citations',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('citation_text', sa.Text(), nullable=False),
    sa.Column('authors', sa.JSON(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('venue', sa.String(length=500), nullable=True),
    sa.Column('doi', sa.String(length=255), nullable=True),
    sa.Column('url', sa.String(length=1000), nullable=True),
    sa.Column('page_number', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create team_members table
    op.create_table('team_members',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('team_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('joined_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('team_id', 'user_id', name='unique_team_user')
    )

    # Create project_permissions table
    op.create_table('project_permissions',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True),
    sa.Column('team_id', postgresql.UUID(as_uuid=False), nullable=True),
    sa.Column('permission_level', sa.String(length=50), nullable=False),
    sa.Column('granted_at', sa.DateTime(), nullable=False),
    sa.Column('granted_by', postgresql.UUID(as_uuid=False), nullable=False),
    sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create exports table
    op.create_table('exports',
    sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('created_by', postgresql.UUID(as_uuid=False), nullable=False),
    sa.Column('format', sa.Enum('JSON', 'MARKDOWN', 'HTML', 'PDF', name='exportformat'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='exportstatus'), nullable=False),
    sa.Column('config', sa.JSON(), nullable=True),
    sa.Column('file_path', sa.String(length=1000), nullable=True),
    sa.Column('error', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)
    op.create_index(op.f('ix_cells_project_id'), 'cells', ['project_id'], unique=False)
    op.create_index(op.f('ix_exports_project_id'), 'exports', ['project_id'], unique=False)
    op.create_index(op.f('ix_exports_created_by'), 'exports', ['created_by'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_exports_created_by'), table_name='exports')
    op.drop_index(op.f('ix_exports_project_id'), table_name='exports')
    op.drop_index(op.f('ix_cells_project_id'), table_name='cells')
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_index(op.f('ix_users_email'), table_name='users')

    # Drop tables in reverse order of creation
    op.drop_table('exports')
    op.drop_table('project_permissions')
    op.drop_table('team_members')
    op.drop_table('citations')
    op.drop_table('annotations')
    op.drop_table('documents')
    op.drop_table('cell_outputs')
    op.drop_table('cells')
    op.drop_table('projects')
    op.drop_table('teams')
    op.drop_table('users')

    # Drop enums
    sa.Enum(name='exportformat').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='exportstatus').drop(op.get_bind(), checkfirst=True)
