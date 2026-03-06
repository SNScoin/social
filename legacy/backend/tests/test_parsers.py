import asyncio
import logging
from backend.app.parsers.facebook_parser import FacebookParser
from parsers.tiktok_parser import TikTokParser
from backend.app.parsers.instagram_parser import InstagramParser
from parsers.youtube_parser import YouTubeParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test URLs
TEST_URLS = {
    'facebook': 'https://www.facebook.com/reel/3139447296208152',
    'tiktok': 'https://www.tiktok.com/@tiktok/video/7316780105202765102',
    'instagram': 'https://www.instagram.com/reel/C4Yz123ABC/',
    'youtube': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
}

async def test_parser(platform: str, parser, url: str):
    """Test a specific parser with a URL"""
    logger.info(f"\nTesting {platform.upper()} Parser")
    logger.info(f"URL: {url}")
    
    # Test URL validation
    is_valid = parser.validate_url(url)
    logger.info(f"URL Valid: {is_valid}")
    
    # Test ID extraction
    content_id = parser.extract_id(url)
    logger.info(f"Extracted ID: {content_id}")
    
    # Test full parsing
    try:
        result = await parser.parse_url(url)
        logger.info("\nParse Result:")
        logger.info(f"Title: {result.get('title', 'N/A')}")
        logger.info(f"Owner: {result.get('owner', 'N/A')}")
        logger.info(f"Views: {result.get('views', 'N/A')}")
        logger.info(f"Likes: {result.get('likes', 'N/A')}")
        logger.info(f"Comments: {result.get('comments', 'N/A')}")
        logger.info(f"Created Time: {result.get('created_time', 'N/A')}")
        logger.info(f"Hashtags: {', '.join(result.get('hashtags', []))}")
        logger.info(f"Platform: {result.get('platform', 'N/A')}")
        if 'error' in result:
            logger.warning(f"\nError Message: {result['error']}")
    except Exception as e:
        logger.error(f"Error parsing URL: {str(e)}")

async def main():
    """Test all parsers"""
    parsers = {
        'facebook': FacebookParser(),
        'tiktok': TikTokParser(),
        'instagram': InstagramParser(),
        'youtube': YouTubeParser()
    }
    
    for platform, url in TEST_URLS.items():
        if platform in parsers:
            await test_parser(platform, parsers[platform], url)
        else:
            logger.warning(f"No parser found for platform: {platform}")

if __name__ == "__main__":
    asyncio.run(main()) 