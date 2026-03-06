"""merge heads

Revision ID: merge_heads
Revises: add_column_mapping_fields, add_facebook_platform
Create Date: 2024-03-19 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('add_column_mapping_fields', 'add_facebook_platform')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 