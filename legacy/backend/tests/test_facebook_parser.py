from backend.app.parsers.facebook_parser import FacebookParser
import logging
import asyncio
import os

# Set the API key for testing
os.environ["FACEBOOK_RAPIDAPI_KEY"] = "686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_facebook_parser():
    # Test URL
    test_url = "https://www.facebook.com/reel/1699028237419497"
    
    parser = FacebookParser()
    
    logger.info(f"\nTesting Facebook Parser")
    logger.info(f"URL: {test_url}")
    
    # Test URL validation
    is_valid = parser.validate_url(test_url)
    logger.info(f"URL Valid: {is_valid}")
    
    # Test ID extraction
    video_id = parser.extract_id(test_url)
    logger.info(f"Extracted Video ID: {video_id}")
    
    # Test full parsing
    try:
        result = await parser.parse_url(test_url)
        logger.info("\nParse Result:")
        logger.info(f"Title/Message: {result.get('title', 'N/A')}")
        logger.info(f"Owner: {result.get('owner', 'N/A')}")
        logger.info(f"Views: {result.get('views', 'N/A')}")
        logger.info(f"Likes/Reactions: {result.get('likes', 'N/A')}")
        logger.info(f"Comments: {result.get('comments', 'N/A')}")
        logger.info(f"Shares: {result.get('shares', 'N/A')}")
        logger.info(f"Created Time: {result.get('created_time', 'N/A')}")
        logger.info(f"Hashtags: {', '.join(result.get('hashtags', []))}")
        logger.info(f"Platform: {result.get('platform', 'N/A')}")
        if 'error' in result:
            logger.warning(f"\nError Message: {result['error']}")
        
        # Test basic metrics
        assert result is not None
        assert result["title"] is not None
        assert result["likes"] > 0
        assert result["comments"] >= 0
        assert isinstance(result["hashtags"], list)
        assert result["owner"] is not None
        
        # Test view count handling
        assert "views" in result
        assert "video_play_count" in result  # New field for additional context
        
        # If view count is present, it should be a non-negative integer
        if result["views"] is not None:
            assert isinstance(result["views"], int)
            assert result["views"] >= 0
        
        # If video_play_count is present, it should be a non-negative integer
        if result["video_play_count"] is not None:
            assert isinstance(result["video_play_count"], int)
            assert result["video_play_count"] >= 0
    except Exception as e:
        logger.error(f"Error parsing URL: {str(e)}")
        logger.error(f"Full error details:", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(test_facebook_parser())
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}", exc_info=True) 