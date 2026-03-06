from backend.app.db.database import engine
from backend.app.models.models import Base, MondayConnection

def create_monday_table():
    # Create the monday_connections table
    MondayConnection.__table__.create(engine)

if __name__ == "__main__":
    create_monday_table()
    print("Monday connections table created successfully!") 