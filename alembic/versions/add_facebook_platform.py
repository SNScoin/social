"""add facebook platform

Revision ID: add_facebook_platform
Revises: monday_fields_combined
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_facebook_platform'
down_revision = 'monday_fields_combined'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum type if it doesn't exist
    platform_enum = postgresql.ENUM('youtube', 'tiktok', 'instagram', 'facebook', name='platform')
    platform_enum.create(op.get_bind(), checkfirst=True)
    
    # Update the platform column in links table to use the enum
    op.alter_column('links', 'platform',
        existing_type=sa.String(),
        type_=sa.Enum('youtube', 'tiktok', 'instagram', 'facebook', name='platform'),
        existing_nullable=False,
        postgresql_using="platform::platform"
    )

def downgrade():
    # Convert back to string type
    op.alter_column('links', 'platform',
        existing_type=sa.Enum('youtube', 'tiktok', 'instagram', 'facebook', name='platform'),
        type_=sa.String(),
        existing_nullable=False
    )
    
    # Drop the enum type
    platform_enum = postgresql.ENUM('youtube', 'tiktok', 'instagram', 'facebook', name='platform')
    platform_enum.drop(op.get_bind()) 