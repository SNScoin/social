"""add is_active column to users

Revision ID: add_is_active_column
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_active_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add is_active column with default value True
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    # Remove is_active column
    op.drop_column('users', 'is_active') 