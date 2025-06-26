import os
import psycopg2
from dotenv import load_dotenv
import bcrypt

load_dotenv()

DB_NAME = os.getenv('POSTGRES_DB', 'social_stats')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '123Panda1313!')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

USERNAME = 'testuser'
EMAIL = 'test@example.com'
PASSWORD = 'testpassword123'

hashed_password = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO users (username, email, hashed_password, is_active)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """, (USERNAME, EMAIL, hashed_password, True))
    conn.commit()
    print(f"User '{USERNAME}' added or already exists.")
    except Exception as e:
    print(f"Error: {e}")
    finally:
    cur.close()
    conn.close() 