"""Add company_id to monday_connections

Revision ID: add_company_to_monday
Revises: monday_fields_combined
Create Date: 2024-04-10 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, text

# revision identifiers, used by Alembic.
revision = 'add_company_to_monday'
down_revision = 'monday_fields_combined'
branch_labels = None
depends_on = None

def upgrade():
    # Add company_id column as nullable first
    op.add_column('monday_connections', sa.Column('company_id', sa.Integer(), nullable=True))
    
    # Create a default company if it doesn't exist
    op.execute(text("""
        INSERT INTO companies (name, created_at)
        SELECT 'Default Company', NOW()
        WHERE NOT EXISTS (SELECT 1 FROM companies WHERE name = 'Default Company')
        RETURNING id;
    """))
    
    # Get the default company id
    result = op.get_bind().execute(text("SELECT id FROM companies WHERE name = 'Default Company'"))
    default_company_id = result.scalar()
    
    # Update existing records with the default company
    op.execute(text(f"""
        UPDATE monday_connections 
        SET company_id = :company_id
        WHERE company_id IS NULL
    """).bindparams(company_id=default_company_id))
    
    # Add foreign key constraint with a clear name
    op.create_foreign_key(
        'fk_monday_connections_company_id_companies',
        'monday_connections',
        'companies',
        ['company_id'],
        ['id']
    )
    
    # Make company_id not nullable after data migration
    op.alter_column('monday_connections', 'company_id',
                    existing_type=sa.Integer(),
                    nullable=False)

def downgrade():
    # Make company_id nullable first
    op.alter_column('monday_connections', 'company_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # Remove foreign key constraint
    op.drop_constraint('fk_monday_connections_company_id_companies', 'monday_connections', type_='foreignkey')
    
    # Remove company_id column
    op.drop_column('monday_connections', 'company_id') 