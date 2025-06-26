import asyncio
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal, engine, SQLALCHEMY_DATABASE_URL
from backend.app.models.models import Base, Link, LinkMetrics
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_insert():
    logger.info(f"Testing database connection with URL: {SQLALCHEMY_DATABASE_URL}")
    
    try:
        # Test database connection
        with engine.connect() as connection:
            logger.info("Successfully connected to database")
            
        # Create tables if they don't exist
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create a new database session
        db = SessionLocal()
        
        try:
            # Test data
            test_url = "https://www.tiktok.com/@tiktok/video/7321803408461325614"
            test_platform = "tiktok"
            test_title = "Test TikTok Video"
            test_user_id = 1  # Make sure this user exists in your database
            test_company_id = 2  # Make sure this company exists in your database
            
            logger.info(f"Creating new link with URL: {test_url}")
            
            # Create new link
            new_link = Link(
                url=test_url,
                platform=test_platform,
                title=test_title,
                user_id=test_user_id,
                company_id=test_company_id,
                created_at=datetime.utcnow()
            )
            
            # Add link to database
            db.add(new_link)
            db.commit()
            db.refresh(new_link)
            
            logger.info(f"Successfully created link with ID: {new_link.id}")
            
            # Create metrics for the link
            logger.info("Creating metrics for the link...")
            new_metrics = LinkMetrics(
                link_id=new_link.id,
                views=1000,
                likes=500,
                comments=100,
                updated_at=datetime.utcnow()
            )
            
            # Add metrics to database
            db.add(new_metrics)
            db.commit()
            
            logger.info(f"Successfully created metrics for link ID: {new_link.id}")
            
            # Verify the data was inserted
            link = db.query(Link).filter(Link.id == new_link.id).first()
            metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == new_link.id).first()
            
            logger.info("\nVerification:")
            logger.info(f"Link: {link.url} (ID: {link.id})")
            logger.info(f"Metrics: views={metrics.views}, likes={metrics.likes}, comments={metrics.comments}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        test_db_insert()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise 