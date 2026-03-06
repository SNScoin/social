import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('POSTGRES_DB', 'social_stats')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '123Panda1313!')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Check company_id=1
cur.execute("SELECT id, name FROM companies WHERE id = 1;")
company = cur.fetchone()
if company:
    print(f"Company found: id={company[0]}, name={company[1]}")
else:
    print("Company with id=1 does NOT exist.")

# Check testuser in users
cur.execute("SELECT id, username, email FROM users WHERE username = 'testuser' OR email = 'testuser';")
user = cur.fetchone()
if user:
    print(f"User found: id={user[0]}, username={user[1]}, email={user[2]}")
else:
    print("User 'testuser' does NOT exist.")

cur.close()
conn.close() 