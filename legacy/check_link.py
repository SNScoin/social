import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_NAME = os.getenv('POSTGRES_DB', 'social_stats')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '123Panda1313!')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

def check_link(link_id):
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
        cur.execute('SELECT id, url, platform, title FROM links WHERE id = %s', (link_id,))
        
        # Fetch the row
        row = cur.fetchone()
        
        if row:
            id, url, platform, title = row
            print('\nLink details:')
            print('-' * 80)
            print(f"ID: {id}")
            print(f"URL: {url}")
            print(f"Platform: {platform}")
            print(f"Title: {title}")
            print('-' * 80)
        else:
            print(f"No link found with ID {link_id}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_link(17) 