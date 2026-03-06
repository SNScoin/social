from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123Panda1313!@localhost:5432/social_stats"
)

def test_db_connection():
    logger.info(f"Testing database connection with URL: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            # Try a simple query
            result = connection.execute(text("SELECT 1"))
            logger.info("Successfully connected to database")
            
            # Test if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"Existing tables: {tables}")
            
            # Test if users exist
            result = connection.execute(text("SELECT id, email FROM users"))
            users = [{"id": row[0], "email": row[1]} for row in result]
            logger.info(f"Existing users: {users}")
            
            # Test if companies exist
            result = connection.execute(text("SELECT id, name, owner_id FROM companies"))
            companies = [{"id": row[0], "name": row[1], "owner_id": row[2]} for row in result]
            logger.info(f"Existing companies: {companies}")
            
            # Try to insert a test link
            try:
                result = connection.execute(text("""
                    INSERT INTO links (url, platform, title, user_id, company_id, created_at)
                    VALUES (:url, :platform, :title, :user_id, :company_id, :created_at)
                    RETURNING id
                """), {
                    "url": "https://www.tiktok.com/@tiktok/video/7321803408461325614",
                    "platform": "tiktok",
                    "title": "Test TikTok Video",
                    "user_id": 1,  # Make sure this user exists
                    "company_id": 2,  # Make sure this company exists
                    "created_at": datetime.utcnow()
                })
                link_id = result.scalar()
                logger.info(f"Successfully inserted test link with ID: {link_id}")
                
                # Insert test metrics
                result = connection.execute(text("""
                    INSERT INTO link_metrics (link_id, views, likes, comments, updated_at)
                    VALUES (:link_id, :views, :likes, :comments, :updated_at)
                    RETURNING id
                """), {
                    "link_id": link_id,
                    "views": 1000,
                    "likes": 500,
                    "comments": 100,
                    "updated_at": datetime.utcnow()
                })
                metrics_id = result.scalar()
                logger.info(f"Successfully inserted test metrics with ID: {metrics_id}")
                
                # Verify the inserted data
                result = connection.execute(text("""
                    SELECT l.url, l.platform, m.views, m.likes, m.comments
                    FROM links l
                    JOIN link_metrics m ON l.id = m.link_id
                    WHERE l.id = :link_id
                """), {"link_id": link_id})
                row = result.fetchone()
                data = {
                    "url": row[0],
                    "platform": row[1],
                    "views": row[2],
                    "likes": row[3],
                    "comments": row[4]
                }
                logger.info(f"Verified inserted data: {data}")
                
            except Exception as e:
                logger.error(f"Error inserting test data: {str(e)}")
                raise
                
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        test_db_connection()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise 