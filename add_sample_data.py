from backend.app.db.database import SessionLocal
from backend.app.models.models import SocialLink, Platform
from datetime import datetime, timedelta

def add_sample_data():
    db = SessionLocal()
    try:
        # Sample YouTube data
        youtube_links = [
            {
                "platform": Platform.youtube,
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Never Gonna Give You Up",
                "likes": 15000,
                "views": 100000,
                "comments": 500,
                "last_updated": datetime.now() - timedelta(days=1)
            },
            {
                "platform": Platform.youtube,
                "url": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
                "title": "Shape of You",
                "likes": 20000,
                "views": 500000,
                "comments": 1000,
                "last_updated": datetime.now() - timedelta(days=2)
            }
        ]

        # Sample TikTok data
        tiktok_links = [
            {
                "platform": Platform.tiktok,
                "url": "https://www.tiktok.com/@example/video/123456789",
                "title": "Dance Challenge",
                "likes": 5000,
                "views": 20000,
                "comments": 100,
                "last_updated": datetime.now() - timedelta(hours=12)
            }
        ]

        # Sample Instagram data
        instagram_links = [
            {
                "platform": Platform.instagram,
                "url": "https://www.instagram.com/p/ABC123/",
                "title": "Sunset Photo",
                "likes": 1000,
                "views": 5000,
                "comments": 50,
                "last_updated": datetime.now() - timedelta(hours=6)
            }
        ]

        # Add all sample data
        for link_data in youtube_links + tiktok_links + instagram_links:
            link = SocialLink(**link_data)
            db.add(link)

        db.commit()
        print("✅ Sample data added successfully!")
    except Exception as e:
        print(f"❌ Error adding sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data() 