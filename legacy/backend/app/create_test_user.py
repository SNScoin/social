from models.models import User
from db.database import SessionLocal
from core.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("Test user already exists")
            return existing_user
        
        # Create test user
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password=get_password_hash("testpass"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print("Test user created successfully")
        return test_user
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 