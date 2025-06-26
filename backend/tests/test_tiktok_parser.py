import logging

# Set up logging to print INFO and above to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

import asyncio
from backend.app.parsers.tiktok_parser import TikTokParser
import time

logger = logging.getLogger(__name__)

async def test_tiktok_parser():
    parser = TikTokParser()
    
    # Test with the provided TikTok video link
    test_urls = [
        "https://www.tiktok.com/@quran_karim_academy/video/7487533914215468319?is_from_webapp=1&sender_device=pc"
    ]
    
    for url in test_urls:
        try:
            logger.info(f"\nTesting URL: {url}")
            start_time = time.time()
            
        # Test URL validation
            is_valid = parser.validate_url(url)
            logger.info(f"URL validation: {'Valid' if is_valid else 'Invalid'}")
            
            if is_valid:
        # Test video ID extraction
                video_id = parser._extract_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        
                if video_id:
        # Test full parsing
                    result = await parser.parse_url(url)
        
                    # Print results
                    logger.info("Parsing Results:")
                    logger.info(f"Title: {result.get('title', 'N/A')}")
                    logger.info(f"Description: {result.get('description', 'N/A')}")
                    logger.info(f"Views: {result.get('views', 'N/A'):,}")
                    logger.info(f"Likes: {result.get('likes', 'N/A'):,}")
                    logger.info(f"Comments: {result.get('comments', 'N/A'):,}")
                    logger.info(f"Owner: {result.get('owner', 'N/A')}")
                    logger.info(f"Hashtags: {result.get('hashtags', [])}")
                    
                    end_time = time.time()
                    logger.info(f"Total processing time: {end_time - start_time:.2f} seconds")
                else:
                    logger.error("Failed to extract video ID")
            else:
                logger.error("Invalid URL format")
        
    except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        logger.info("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_tiktok_parser()) 