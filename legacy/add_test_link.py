from backend.app.db.database import SessionLocal
from backend.app.models.models import SocialLink, Platform
from datetime import datetime

def add_test_link():
    db = SessionLocal()
    try:
        # Create a test Facebook link
        test_link = SocialLink(
            url="https://www.facebook.com/reel/123456789",
            platform=Platform.facebook,
            title="Test Facebook Reel",
            views=1000,
            likes=500,
            comments=50,
            is_processed=True,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        db.add(test_link)
        db.commit()
        print("Test Facebook link added successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding test link: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    add_test_link() 