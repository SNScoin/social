from database import engine
from sqlalchemy import text

try:
    # Try to connect to the database
    with engine.connect() as connection:
        # Execute a simple query
        result = connection.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print("PostgreSQL version:", connection.execute(text("SELECT version()")).scalar())
except Exception as e:
    print("❌ Database connection failed!")
    print("Error:", str(e)) 