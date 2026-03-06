import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def add_user_profile_fields():
    """Add new profile fields to users table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Add new columns to users table
        try:
            # Add display_name column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR"))
            print("✓ Added display_name column")
            
            # Add profile_picture column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR"))
            print("✓ Added profile_picture column")
            
            # Add bio column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT"))
            print("✓ Added bio column")
            
            # Add timezone column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR DEFAULT 'UTC'"))
            print("✓ Added timezone column")
            
            # Add email_verified column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE"))
            print("✓ Added email_verified column")
            
            # Add last_login column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE"))
            print("✓ Added last_login column")
            
            conn.commit()
            print("✅ All user profile fields added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_user_profile_fields() 