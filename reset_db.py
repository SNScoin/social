from sqlalchemy import text
from backend.app.db.database import engine
from backend.app.models.models import Base

def reset_database():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("All tables recreated successfully")

if __name__ == "__main__":
    reset_database() 