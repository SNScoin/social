import asyncio
import logging
from backend.app.parsers.tiktok_parser import TikTokParser
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_tiktok_parser():
    try:
        # Initialize parser
        parser = TikTokParser()
        logger.info("TikTok parser initialized")
        
        # Test URL
        test_url = "https://www.tiktok.com/@abo._.fathy/video/7501331317657718034"
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing URL: {test_url}")
        
        # Validate URL
        if not parser.validate_url(test_url):
            logger.error(f"Invalid TikTok URL: {test_url}")
            return
        
        # Parse URL
        try:
            data = await parser.parse_url(test_url)
            
            # Log results in a structured way
            logger.info("\nParsed TikTok data:")
            logger.info(json.dumps(data, indent=2))
            
            # Verify all required fields are present
            required_fields = ['title', 'views', 'likes', 'comments', 'owner', 'created_time', 'hashtags']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                logger.warning(f"Missing fields in response: {missing_fields}")
            else:
                logger.info("All required fields are present")
            
            # Verify data types
            assert isinstance(data['views'], (int, float)), "Views should be a number"
            assert isinstance(data['likes'], (int, float)), "Likes should be a number"
            assert isinstance(data['comments'], (int, float)), "Comments should be a number"
            assert isinstance(data['hashtags'], list), "Hashtags should be a list"
            
            logger.info("Data type validation passed")
            
        except Exception as e:
            logger.error(f"Error processing URL {test_url}: {str(e)}")
            return
        
        logger.info(f"Successfully tested URL: {test_url}")
        logger.info(f"{'='*50}\n")
    
    except Exception as e:
        logger.error(f"Error in test execution: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_tiktok_parser()) 