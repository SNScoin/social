from database import SessionLocal
from backend.app.models.models import SocialLink
from social_parser import SocialMediaParser
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_unprocessed_links():
    db = SessionLocal()
    parser = SocialMediaParser()
    
    try:
        # Get all unprocessed links
        unprocessed_links = db.query(SocialLink).filter_by(is_processed=False).all()
        
        for link in unprocessed_links:
            logger.info(f"Processing link: {link.url}")
            try:
                # Detect platform
                if 'youtube.com' in link.url or 'youtu.be' in link.url:
                    link.platform = 'youtube'
                elif 'tiktok.com' in link.url:
                    link.platform = 'tiktok'
                elif 'instagram.com' in link.url:
                    link.platform = 'instagram'
                elif 'facebook.com' in link.url or 'fb.watch' in link.url:
                    link.platform = 'facebook'
                else:
                    logger.warning(f"Unknown platform for URL: {link.url}")
                    continue

                # Get metrics
                stats = parser.parse_link(link.url)
                if stats:
                    link.title = stats.get('title', '')
                    link.views = stats.get('views', 0)
                    link.likes = stats.get('likes', 0)
                    link.comments = stats.get('comments', 0)
                    link.is_processed = True
                    link.last_updated = datetime.utcnow()
                    logger.info(f"Successfully processed {link.url}")
                else:
                    logger.error(f"Could not get stats for {link.url}")

            except Exception as e:
                logger.error(f"Error processing {link.url}: {str(e)}")
                continue

            # Sleep briefly to avoid rate limiting
            time.sleep(1)

        db.commit()
        logger.info("Finished processing links")

    except Exception as e:
        logger.error(f"Error in process_unprocessed_links: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    while True:
        process_unprocessed_links()
        logger.info("Sleeping for 60 seconds...")
        time.sleep(60)  # Wait for 60 seconds before next run 