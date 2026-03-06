import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_NAME = os.getenv('POSTGRES_DB', 'social_stats')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '123Panda1313!')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

COMPANY_ID = 1

def list_company_links():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute query
        cur.execute('''
            SELECT id, url, platform, title, created_at 
            FROM links 
            WHERE company_id = %s 
            ORDER BY created_at DESC
        ''', (COMPANY_ID,))
        
        # Fetch all rows
        rows = cur.fetchall()
        
        # Print header
        print('\nLinks for Company ID:', COMPANY_ID)
        print('-' * 100)
        print(f"{'ID':<5} | {'Platform':<10} | {'Title':<30} | {'URL':<40}")
        print('-' * 100)
        
        # Print each row
        for row in rows:
            id, url, platform, title, created_at = row
            print(f"{id:<5} | {platform:<10} | {title[:30]:<30} | {url:<40}")
        
        print('-' * 100)
        print(f"Total links found: {len(rows)}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    list_company_links() 