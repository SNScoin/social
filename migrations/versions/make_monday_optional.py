"""make monday configuration optional

Revision ID: make_monday_optional
Revises: add_is_active_column
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'make_monday_optional'
down_revision = 'add_is_active_column'
branch_labels = None
depends_on = None

def upgrade():
    # Make api_token nullable
    op.alter_column('monday_connections', 'api_token',
                    existing_type=sa.String(),
                    nullable=True)
    
    # Make company_id nullable
    op.alter_column('monday_connections', 'company_id',
                    existing_type=sa.Integer(),
                    nullable=True)

def downgrade():
    # Make api_token non-nullable again
    op.alter_column('monday_connections', 'api_token',
                    existing_type=sa.String(),
                    nullable=False)
    
    # Make company_id non-nullable again
    op.alter_column('monday_connections', 'company_id',
                    existing_type=sa.Integer(),
                    nullable=False) 