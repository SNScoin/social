from backend.app.db.database import SessionLocal
from backend.app.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_password():
    db = SessionLocal()
    try:
        # Get the test user
        user = db.query(User).filter(User.username == "testuser").first()
        if user:
            print(f"User found: {user.username}")
            print(f"Stored password hash: {user.hashed_password}")
            # Verify the password
            is_valid = pwd_context.verify("test123", user.hashed_password)
            print(f"Password 'test123' is valid: {is_valid}")
        else:
            print("Test user not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_password() 