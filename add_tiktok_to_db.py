import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.models import Link, LinkMetrics, Company
from backend.app.parsers.tiktok_parser import TikTokParser
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:123Panda1313!@localhost:5432/social_stats')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

async def add_tiktok_to_db():
    try:
        # Initialize parser
        parser = TikTokParser()
        logger.info("TikTok parser initialized")
        
        # Test URL
        tiktok_url = "https://www.tiktok.com/@abo._.fathy/video/7501331317657718034"
        company_id = 2
        
        # Create database session
        session = Session()
        
        try:
            # Verify company exists
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                logger.error(f"Company {company_id} not found")
                return
            
            # Check if link already exists
            existing_link = session.query(Link).filter(
                Link.url == tiktok_url,
                Link.company_id == company_id
            ).first()
            
            if existing_link:
                logger.warning(f"Link already exists: {tiktok_url}")
                return
            
            # Parse TikTok data
            logger.info(f"Parsing TikTok URL: {tiktok_url}")
            data = await parser.parse_url(tiktok_url)
            
            # Create link
            db_link = Link(
                url=tiktok_url,
                platform='tiktok',
                title=data.get('title', ''),
                user_id=1,  # Using default user ID
                company_id=company_id
            )
            session.add(db_link)
            session.commit()
            session.refresh(db_link)
            
            # Create metrics
            db_metrics = LinkMetrics(
                link_id=db_link.id,
                views=data.get('views', 0),
                likes=data.get('likes', 0),
                comments=data.get('comments', 0)
            )
            session.add(db_metrics)
            session.commit()
            
            logger.info(f"Successfully added TikTok video to company {company_id}")
            logger.info(f"Link ID: {db_link.id}")
            logger.info(f"Metrics: views={data.get('views')}, likes={data.get('likes')}, comments={data.get('comments')}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding TikTok to database: {str(e)}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(add_tiktok_to_db()) 