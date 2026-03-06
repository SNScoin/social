from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_monday_optional():
    try:
        with engine.connect() as connection:
            # Make Monday configuration fields optional
            connection.execute(text("""
                ALTER TABLE monday_connections 
                ALTER COLUMN api_token DROP NOT NULL,
                ALTER COLUMN company_id DROP NOT NULL,
                ALTER COLUMN workspace_id DROP NOT NULL,
                ALTER COLUMN workspace_name DROP NOT NULL,
                ALTER COLUMN board_id DROP NOT NULL,
                ALTER COLUMN board_name DROP NOT NULL,
                ALTER COLUMN item_id DROP NOT NULL,
                ALTER COLUMN item_name DROP NOT NULL,
                ALTER COLUMN views_column_id DROP NOT NULL,
                ALTER COLUMN views_column_name DROP NOT NULL,
                ALTER COLUMN likes_column_id DROP NOT NULL,
                ALTER COLUMN likes_column_name DROP NOT NULL,
                ALTER COLUMN comments_column_id DROP NOT NULL,
                ALTER COLUMN comments_column_name DROP NOT NULL;
            """))
            connection.commit()
            logger.info("Successfully made Monday configuration fields optional")
    except Exception as e:
        logger.error(f"Error making Monday configuration optional: {str(e)}")
        raise

if __name__ == "__main__":
    make_monday_optional() 