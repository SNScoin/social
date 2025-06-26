"""Add Monday.com fields combined

Revision ID: monday_fields_combined
Revises: create_tables
Create Date: 2024-04-10 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'monday_fields_combined'
down_revision = 'create_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Get database connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Check if monday_connections table exists
    if 'monday_connections' not in inspector.get_table_names():
        # Create monday_connections table if it doesn't exist
        op.create_table(
            'monday_connections',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('api_token', sa.String(), nullable=False),
            sa.Column('workspace_id', sa.String(length=255), nullable=True),
            sa.Column('workspace_name', sa.String(length=255), nullable=True),
            sa.Column('board_id', sa.String(length=255), nullable=True),
            sa.Column('board_name', sa.String(length=255), nullable=True),
            sa.Column('item_id', sa.String(length=255), nullable=True),
            sa.Column('item_name', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # Add new columns if they don't exist
        existing_columns = [col['name'] for col in inspector.get_columns('monday_connections')]
        
        if 'workspace_id' not in existing_columns:
            op.add_column('monday_connections', sa.Column('workspace_id', sa.String(length=255), nullable=True))
        if 'workspace_name' not in existing_columns:
            op.add_column('monday_connections', sa.Column('workspace_name', sa.String(length=255), nullable=True))
        if 'board_id' not in existing_columns:
            op.add_column('monday_connections', sa.Column('board_id', sa.String(length=255), nullable=True))
        if 'board_name' not in existing_columns:
            op.add_column('monday_connections', sa.Column('board_name', sa.String(length=255), nullable=True))
        if 'item_id' not in existing_columns:
            op.add_column('monday_connections', sa.Column('item_id', sa.String(length=255), nullable=True))
        if 'item_name' not in existing_columns:
            op.add_column('monday_connections', sa.Column('item_name', sa.String(length=255), nullable=True))

def downgrade():
    # Drop the new columns first
    op.drop_column('monday_connections', 'workspace_id')
    op.drop_column('monday_connections', 'workspace_name')
    op.drop_column('monday_connections', 'board_id')
    op.drop_column('monday_connections', 'board_name')
    op.drop_column('monday_connections', 'item_id')
    op.drop_column('monday_connections', 'item_name') 