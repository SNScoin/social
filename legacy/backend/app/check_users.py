from models.models import User
from db.database import SessionLocal
from core.auth import verify_password

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Is Active: {user.is_active}")
            print(f"Created At: {user.created_at}")
            print("---")
    except Exception as e:
        print(f"Error checking users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 