"""Create all tables

Revision ID: create_tables
Revises: 31523148ce6e
Create Date: 2024-04-10 15:51:27.586748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'create_tables'
down_revision: str = '31523148ce6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(), unique=True, index=True),
        sa.Column('email', sa.String(), unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create links table
    op.create_table(
        'links',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('title', sa.String()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create link_metrics table
    op.create_table(
        'link_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('link_id', sa.Integer(), sa.ForeignKey('links.id')),
        sa.Column('views', sa.Integer(), default=0),
        sa.Column('likes', sa.Integer(), default=0),
        sa.Column('comments', sa.Integer(), default=0),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    pass


def downgrade() -> None:
    # op.drop_table('link_metrics')
    # op.drop_table('links')
    # op.drop_table('companies')
    # op.drop_table('users')
    pass 