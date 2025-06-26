from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal
from backend.app.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_root_user():
    db = SessionLocal()
    try:
        # Check if root user already exists
        existing_user = db.query(User).filter(User.username == "ROOT").first()
        if existing_user:
            print("Root user already exists")
            return
        
        # Create root user
        hashed_password = pwd_context.hash("admin123")
        root_user = User(
            username="ROOT",
            email="root@admin.com",
            hashed_password=hashed_password
        )
        db.add(root_user)
        db.commit()
        print("Root user created successfully")
    except Exception as e:
        print(f"Error creating root user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_root_user() 