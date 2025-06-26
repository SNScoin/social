"""add monday_item_id

Revision ID: add_monday_item_id
Revises: 
Create Date: 2024-05-06 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_monday_item_id'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add monday_item_id column to links table
    op.add_column('links', sa.Column('monday_item_id', sa.String(), nullable=True))
    
    # Add updated_at column to links table
    op.add_column('links', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Create monday_configs table
    op.create_table('monday_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('board_id', sa.String(), nullable=True),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monday_configs_id'), 'monday_configs', ['id'], unique=False)
    pass

def downgrade() -> None:
    # Drop monday_configs table
    # op.drop_index(op.f('ix_monday_configs_id'), table_name='monday_configs')
    # op.drop_table('monday_configs')
    
    # Drop columns from links table
    op.drop_column('links', 'updated_at')
    op.drop_column('links', 'monday_item_id')
    pass 