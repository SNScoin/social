import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.instagram_parser import InstagramParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_instagram_parser():
    """Test Instagram parser directly"""
    try:
        # Test with the real Instagram URL
        url = "https://www.instagram.com/p/DJTxMx6NAUq"
        
        logger.info(f"Testing Instagram parser with URL: {url}")
        
        # Create parser instance
        parser = InstagramParser()
        
        # Test URL validation
        is_valid = parser.validate_url(url)
        logger.info(f"URL validation result: {is_valid}")
        
        if not is_valid:
            logger.error("URL validation failed")
            return
        
        # Test parsing
        logger.info("Starting to parse Instagram URL...")
        result = await parser.parse_url(url)
        
        logger.info(f"Parser result: {result}")
        
        if result:
            title = result.get('title', 'NO TITLE')
            views = result.get('views', 0)
            likes = result.get('likes', 0)
            comments = result.get('comments', 0)
            
            logger.info(f"Title: '{title}'")
            logger.info(f"Views: {views}")
            logger.info(f"Likes: {likes}")
            logger.info(f"Comments: {comments}")
            
            if title and title != 'NO TITLE' and title.strip():
                logger.info("✅ SUCCESS: Title extracted successfully")
            else:
                logger.warning("⚠️  WARNING: No title extracted")
        else:
            logger.error("❌ FAILED: Parser returned None")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 