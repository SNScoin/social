import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
import traceback
from database import SessionLocal
from models.models import Link, LinkMetrics, User
from parsers.parser_factory import ParserFactory
from utils.monday_sync import sync_link_to_monday

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'link_processor.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def process_link(link: Link, parser_factory: ParserFactory, db: Session):
    """Process a single link and update its metadata"""
    try:
        logger.info(f"Starting to process link ID {link.id}: {link.url}")
        
        # Get the appropriate parser
        parser = parser_factory.get_parser(link.url)
        if not parser:
            logger.error(f"No parser found for URL: {link.url}")
            return
            
        logger.info(f"Using parser: {parser.__class__.__name__}")
        
        # Parse the URL
        logger.info(f"Fetching metadata for URL: {link.url}")
        metadata = await parser.parse_url(link.url)
        logger.info(f"Received metadata: {metadata}")
        
        # Update link with metadata
        logger.info(f"Updating link ID {link.id} with new metadata")
        
        # Get or create metrics
        metrics = link.metrics
        if not metrics:
            metrics = LinkMetrics(link_id=link.id)
            db.add(metrics)
            link.metrics = metrics
        
        # Convert string values to integers if they're strings
        try:
            metrics.views = int(metadata.get('views', 0))
            metrics.likes = int(metadata.get('likes', 0))
            metrics.comments = int(metadata.get('comments', 0))
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting metrics to integers: {e}")
            metrics.views = 0
            metrics.likes = 0
            metrics.comments = 0
            
        link.title = metadata.get('title', '')
        link.updated_at = datetime.utcnow()
        
        # Explicitly flush changes to ensure they're sent to the database
        db.flush()
        db.commit()
        
        logger.info(f"Successfully updated link ID {link.id}")
        logger.info(f"New values - title: {link.title}, views: {metrics.views}, likes: {metrics.likes}, comments: {metrics.comments}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error processing link {link.url}: {str(e)}", exc_info=True)
        db.rollback()
        raise

async def process_and_sync_link(link: Link, db: Session, user: User = None):
    """Process a link and sync it to Monday.com"""
    try:
        parser_factory = ParserFactory()
        metrics = await process_link(link, parser_factory, db)
        
        if user:
            try:
                logger.info(f"Attempting to sync link {link.id} to Monday.com for user {user.id}")
                await sync_link_to_monday(link, metrics, db, user)
                # Refresh the link to get the updated monday_item_id
                db.refresh(link)
            except Exception as e:
                logger.error(f"Error syncing to Monday.com: {str(e)}", exc_info=True)
                raise
                
        return metrics
        
    except Exception as e:
        logger.error(f"Error processing and syncing link {link.id}: {str(e)}", exc_info=True)
        raise

async def process_unprocessed_links(db: Session) -> None:
    """
    Process all unprocessed links in the database
    """
    try:
        unprocessed_links = db.query(Link).filter(Link.is_processed == False).all()
        for link in unprocessed_links:
            await process_and_sync_link(link, db)
    except Exception as e:
        logging.error(f"Error processing unprocessed links: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting link processor...")
    try:
        asyncio.run(process_unprocessed_links())
    except KeyboardInterrupt:
        logger.info("Link processor stopped by user")
    except Exception as e:
        logger.error(f"Link processor stopped due to error: {str(e)}", exc_info=True) 