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

def list_users():
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
        cur.execute('SELECT id, email, hashed_password FROM users')
        
        # Fetch all rows
        rows = cur.fetchall()
        
        # Print header
        print('\nUsers in database:')
        print('-' * 100)
        print(f"{'ID':<5} | {'Email':<30} | {'Password Hash'}")
        print('-' * 100)
        
        # Print each row
        for row in rows:
            id, email, hashed_password = row
            print(f"{id:<5} | {email:<30} | {hashed_password}")
        
        print('-' * 100)
        print(f"Total users found: {len(rows)}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    list_users() 