"""Add column mapping fields to monday_connections

Revision ID: add_column_mapping_fields
Revises: add_company_to_monday
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_column_mapping_fields'
down_revision = 'add_company_to_monday'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns for column mapping
    op.add_column('monday_connections', sa.Column('views_column_id', sa.String(), nullable=True))
    op.add_column('monday_connections', sa.Column('views_column_name', sa.String(), nullable=True))
    op.add_column('monday_connections', sa.Column('likes_column_id', sa.String(), nullable=True))
    op.add_column('monday_connections', sa.Column('likes_column_name', sa.String(), nullable=True))
    op.add_column('monday_connections', sa.Column('comments_column_id', sa.String(), nullable=True))
    op.add_column('monday_connections', sa.Column('comments_column_name', sa.String(), nullable=True))

def downgrade():
    # Remove the column mapping columns
    op.drop_column('monday_connections', 'views_column_id')
    op.drop_column('monday_connections', 'views_column_name')
    op.drop_column('monday_connections', 'likes_column_id')
    op.drop_column('monday_connections', 'likes_column_name')
    op.drop_column('monday_connections', 'comments_column_id')
    op.drop_column('monday_connections', 'comments_column_name') 