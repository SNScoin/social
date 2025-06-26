"""merge heads final

Revision ID: merge_heads_final
Revises: add_monday_item_id, merge_heads
Create Date: 2024-05-06 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads_final'
down_revision = ('add_monday_item_id', 'merge_heads')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 