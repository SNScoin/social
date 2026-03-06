import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.models import Company, Link, LinkMetrics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_company_links(company_id: int):
    """Check all links and metrics for a specific company."""
    db: Session = SessionLocal()
    try:
        # Get company info
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            logger.error(f"Company with ID {company_id} not found!")
            return
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Company Details:")
        logger.info(f"Name: {company.name}")
        logger.info(f"ID: {company.id}")
        logger.info(f"Owner ID: {company.owner_id}")
        logger.info(f"Created at: {company.created_at}")
        logger.info(f"{'='*50}\n")

        # Get all links for the company
        links = db.query(Link).filter(Link.company_id == company_id).all()
        logger.info(f"Total number of links found: {len(links)}")
        
        # Print details for each link
        for link in links:
            logger.info(f"\n{'-'*50}")
            logger.info(f"Link ID: {link.id}")
            logger.info(f"URL: {link.url}")
            logger.info(f"Platform: {link.platform}")
            logger.info(f"Created at: {link.created_at}")
            logger.info(f"Updated at: {link.updated_at}")
            
            # Get metrics for this link
            metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == link.id).first()
            if metrics:
                logger.info(f"Metrics:")
                logger.info(f"  Views: {metrics.views}")
                logger.info(f"  Likes: {metrics.likes}")
                logger.info(f"  Comments: {metrics.comments}")
                logger.info(f"  Last updated: {metrics.updated_at}")
            else:
                logger.warning("No metrics found for this link!")
            
            logger.info(f"{'-'*50}")

        # Print summary
        logger.info(f"\n{'='*50}")
        logger.info("Summary:")
        logger.info(f"Total links: {len(links)}")
        
        # Count by platform
        platforms = {}
        for link in links:
            platforms[link.platform] = platforms.get(link.platform, 0) + 1
        
        logger.info("\nLinks by platform:")
        for platform, count in platforms.items():
            logger.info(f"{platform}: {count}")
        
        logger.info(f"{'='*50}\n")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting company links check...")
    check_company_links(2)  # Check company with ID 2
    logger.info("Check completed!") 