import psycopg2
import sys
import logging
from datetime import datetime

# Configure logging to write to a file
logging.basicConfig(
    filename='db_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database configuration
DB_CONFIG = {
    'dbname': 'social_stats',
    'user': 'postgres',
    'password': '123Panda1313!',
    'host': 'localhost',
    'port': '5432'
}

def test_db():
    try:
        # Connect to database
        logging.info("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("Connected successfully!")
        
        # Create cursor
        cur = conn.cursor()
        
        try:
            # Test TikTok URL
            url = "https://www.tiktok.com/@tiktok/video/7321803408461325614"
            
            # Insert test link
            logging.info("Inserting test link...")
            cur.execute("""
                INSERT INTO links (url, platform, title, user_id, company_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (url, 'tiktok', 'Test Video', 1, 2, datetime.now()))
            
            link_id = cur.fetchone()[0]
            logging.info(f"Inserted link with ID: {link_id}")
            
            # Insert test metrics
            logging.info("Inserting test metrics...")
            cur.execute("""
                INSERT INTO link_metrics (link_id, views, likes, comments, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (link_id, 1000, 500, 100, datetime.now()))
            
            metrics_id = cur.fetchone()[0]
            logging.info(f"Inserted metrics with ID: {metrics_id}")
            
            # Commit transaction
            conn.commit()
            logging.info("Transaction committed successfully")
            
            # Verify data
            logging.info("Verifying inserted data...")
            cur.execute("""
                SELECT l.url, l.platform, m.views, m.likes, m.comments
                FROM links l
                JOIN link_metrics m ON l.id = m.link_id
                WHERE l.id = %s;
            """, (link_id,))
            
            result = cur.fetchone()
            logging.info(f"Verification result: {result}")
            
            print("Database test completed successfully!")
            print(f"Link ID: {link_id}")
            print(f"Metrics ID: {metrics_id}")
            print(f"Data: {result}")
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error during database operations: {str(e)}")
            print(f"Error: {str(e)}")
            raise
            
        finally:
            cur.close()
            
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        print(f"Connection error: {str(e)}")
        raise
        
    finally:
        if 'conn' in locals():
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    try:
        test_db()
    except Exception as e:
        sys.exit(1)
    sys.exit(0) 