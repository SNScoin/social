from models.models import User, Company
from db.database import SessionLocal

def create_test_company():
    db = SessionLocal()
    try:
        # Get the test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            print("Test user not found")
            return
        
        # Check if test company already exists
        existing_company = db.query(Company).filter(Company.owner_id == test_user.id).first()
        if existing_company:
            print(f"Test company already exists: {existing_company.name}")
            return existing_company
        
        # Create test company
        test_company = Company(
            name="Test Company",
            owner_id=test_user.id
        )
        db.add(test_company)
        db.commit()
        db.refresh(test_company)
        print(f"Test company created successfully: {test_company.name}")
        return test_company
    except Exception as e:
        print(f"Error creating test company: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_company() 