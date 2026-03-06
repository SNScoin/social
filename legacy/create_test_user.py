from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal
from backend.app.models.models import User
from backend.app.core.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("Test user already exists")
            return
        
        # Create test user
        hashed_password = get_password_hash("test123")
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password=hashed_password
        )
        db.add(test_user)
        db.commit()
        print("Test user created successfully")
        print("\nUser details:")
        print(f"Username: testuser")
        print(f"Email: testuser@example.com")
        print(f"Password: test123")
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 