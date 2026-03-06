import psycopg2
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "social_stats"
DB_USER = "postgres"
DB_PASS = "123Panda1313!"

def check_database():
    logger.info("Testing database connection...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        logger.info("Successfully connected to database")
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        logger.info(f"Found tables: {tables}")
        
        # Check users
        cur.execute("SELECT id, email FROM users")
        users = cur.fetchall()
        logger.info(f"Found users: {users}")
        
        # Check companies
        cur.execute("SELECT id, name, owner_id FROM companies")
        companies = cur.fetchall()
        logger.info(f"Found companies: {companies}")
        
        # Insert test TikTok link
        cur.execute("""
            INSERT INTO links (url, platform, title, user_id, company_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            "https://www.tiktok.com/@tiktok/video/7321803408461325614",
            "tiktok",
            "Test TikTok Video",
            1,  # user_id
            2   # company_id
        ))
        link_id = cur.fetchone()[0]
        logger.info(f"Inserted test link with ID: {link_id}")
        
        # Insert test metrics
        cur.execute("""
            INSERT INTO link_metrics (link_id, views, likes, comments)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            link_id,
            1000,
            500,
            100
        ))
        metrics_id = cur.fetchone()[0]
        logger.info(f"Inserted test metrics with ID: {metrics_id}")
        
        # Commit the transaction
        conn.commit()
        
        # Verify the inserted data
        cur.execute("""
            SELECT l.url, l.platform, m.views, m.likes, m.comments
            FROM links l
            JOIN link_metrics m ON l.id = m.link_id
            WHERE l.id = %s
        """, (link_id,))
        data = cur.fetchone()
        logger.info(f"Verified inserted data: {data}")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        logger.error(f"Check failed: {str(e)}")
        raise 