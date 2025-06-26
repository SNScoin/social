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

try:
    cur.execute("DROP TABLE IF EXISTS link_metrics CASCADE;")
    cur.execute("DROP TABLE IF EXISTS links CASCADE;")
    conn.commit()
    print("Dropped link_metrics and links tables.")
except Exception as e:
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close() 