import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.parser_factory import ParserFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_parser_directly(url, platform):
    """Test a parser directly without going through the API"""
    try:
        parser_factory = ParserFactory()
        parser = parser_factory.get_parser(url=url, platform=platform)
        
        if not parser:
            logger.error(f"No parser found for {platform}")
            return None
            
        logger.info(f"Testing {platform} parser with URL: {url}")
        result = await parser.parse_url(url)
        logger.info(f"Parser result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error testing {platform} parser: {str(e)}")
        return None

async def main():
    """Test parsers directly"""
    test_cases = [
        ("https://www.tiktok.com/@tiktok/video/7232187813978351878", "tiktok"),
        ("https://www.instagram.com/p/C4qXqXqXqXq/", "instagram"),
    ]
    
    for url, platform in test_cases:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing {platform.upper()} parser directly")
        logger.info(f"{'='*50}")
        
        result = await test_parser_directly(url, platform)
        if result:
            title = result.get('title', 'NO TITLE')
            logger.info(f"Title: '{title}'")
            if title and title != 'NO TITLE':
                logger.info(f"✅ SUCCESS: Title extracted")
            else:
                logger.warning(f"⚠️  WARNING: No title extracted")
        else:
            logger.error(f"❌ FAILED: Parser failed completely")

if __name__ == "__main__":
    asyncio.run(main()) 