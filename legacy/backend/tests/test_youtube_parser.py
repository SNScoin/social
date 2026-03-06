import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.parsers.youtube_parser import YouTubeParser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_youtube_parser():
    url = "https://www.youtube.com/shorts/2d8apFtA7fY"
    parser = YouTubeParser()
    
    try:
        logger.info(f"Testing YouTube parser with URL: {url}")
        result = await parser.parse_url(url)
        logger.info("Parser result:")
        logger.info(f"Title: {result.get('title', 'No title')}")
        logger.info(f"Views: {result.get('views', 0)}")
        logger.info(f"Likes: {result.get('likes', 0)}")
        logger.info(f"Comments: {result.get('comments', 0)}")
    except Exception as e:
        logger.error(f"Error testing parser: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_youtube_parser()) 