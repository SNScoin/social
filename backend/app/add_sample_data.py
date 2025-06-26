from models.models import User, Company, Link, LinkMetrics
from db.database import SessionLocal
from datetime import datetime, timedelta
import random

def add_sample_data():
    db = SessionLocal()
    try:
        # Get the test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        if not test_user:
            print("Test user not found")
            return
        
        # Get the first company
        company = db.query(Company).filter(Company.owner_id == test_user.id).first()
        if not company:
            print("No company found")
            return
        
        print(f"Adding sample data for company: {company.name}")
        
        # Sample social media links with correct platform names
        sample_links = [
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube",
                "title": "Sample YouTube Video"
            },
            {
                "url": "https://www.tiktok.com/@testuser/video/123456789",
                "platform": "tiktok", 
                "title": "Sample TikTok Video"
            },
            {
                "url": "https://www.instagram.com/p/ABC123/",
                "platform": "instagram",
                "title": "Sample Instagram Post"
            },
            {
                "url": "https://www.facebook.com/testuser/posts/123456789",
                "platform": "facebook",
                "title": "Sample Facebook Post"
            },
            {
                "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
                "platform": "youtube",
                "title": "Another YouTube Video"
            }
        ]
        
        # Add links and metrics
        for i, link_data in enumerate(sample_links):
            # Create link
            link = Link(
                url=link_data["url"],
                platform=link_data["platform"],
                title=link_data["title"],
                user_id=test_user.id,
                company_id=company.id,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(link)
            db.flush()  # Get the link ID
            
            # Create metrics with realistic data
            views = random.randint(1000, 50000)
            likes = random.randint(50, int(views * 0.1))  # 1-10% like rate
            comments = random.randint(10, int(views * 0.02))  # 0.5-2% comment rate
            
            metrics = LinkMetrics(
                link_id=link.id,
                views=views,
                likes=likes,
                comments=comments,
                updated_at=datetime.now() - timedelta(hours=random.randint(1, 24))
            )
            db.add(metrics)
            
            print(f"Added {link_data['platform']} link: {views} views, {likes} likes, {comments} comments")
        
        db.commit()
        print("Sample data added successfully!")
        
    except Exception as e:
        print(f"Error adding sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data() 