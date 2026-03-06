from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_is_active_column():
    try:
        with engine.connect() as connection:
            # Add is_active column if it doesn't exist
            connection.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'is_active'
                    ) THEN
                        ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
                    END IF;
                END $$;
            """))
            connection.commit()
            logger.info("Successfully added is_active column to users table")
    except Exception as e:
        logger.error(f"Error adding is_active column: {str(e)}")
        raise

if __name__ == "__main__":
    add_is_active_column() 