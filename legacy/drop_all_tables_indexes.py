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
    # Drop all tables
    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS "' || r.tablename || '" CASCADE;';
            END LOOP;
        END $$;
    """)
    # Drop all indexes
    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT indexname FROM pg_indexes WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP INDEX IF EXISTS "' || r.indexname || '" CASCADE;';
            END LOOP;
        END $$;
    """)
    conn.commit()
    print("Dropped all tables and indexes in the public schema.")
except Exception as e:
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close() 