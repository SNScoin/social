from backend.app.db.database import SessionLocal
from backend.app.models.models import User
from passlib.context import CryptContext

def check_root_user():
    db = SessionLocal()
    try:
        root_user = db.query(User).filter(User.username == "ROOT").first()
        if root_user:
            print("\nRoot user details:")
            print(f"ID: {root_user.id}")
            print(f"Username: {root_user.username}")
            print(f"Email: {root_user.email}")
            print(f"Created at: {root_user.created_at}")
            print(f"Password hash: {root_user.hashed_password}")
        else:
            print("Root user not found in database.")
    finally:
        db.close()

if __name__ == "__main__":
    check_root_user() 