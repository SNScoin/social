from .youtube_parser import YouTubeParser
from .tiktok_parser import TikTokParser
from .instagram_parser import InstagramParser
from .facebook_parser import FacebookParser
from typing import Optional, Dict
from .base_parser import BaseParser
import logging

logger = logging.getLogger(__name__)

class ParserFactory:
    """Factory class for creating social media parsers"""
    
    def __init__(self):
        self.parsers = {}
        for name, parser_cls in [
            ('youtube', YouTubeParser),
            ('tiktok', TikTokParser),
            ('instagram', InstagramParser),
            ('facebook', FacebookParser)
        ]:
            try:
                self.parsers[name] = parser_cls()
                logger.info(f"ParserFactory: Successfully initialized {name} parser.")
            except Exception as e:
                logger.error(f"ParserFactory: Failed to initialize {name} parser: {e}")
    
    def get_parser(self, url: str = None, platform: str = None) -> Optional[BaseParser]:
        """Get the appropriate parser for the given URL or platform"""
        if platform:
            platform = platform.lower()
            parser = self.parsers.get(platform)
            if parser:
                return parser
            logger.warning(f"No parser found for platform: {platform}")
            return None
        
        if url:
            url = url.lower()
            for key, parser in self.parsers.items():
                if parser.validate_url(url):
                    logger.info(f"Found parser for URL: {url}")
                    return parser
            logger.warning(f"No parser found for URL: {url}")
            return None
        
        logger.error("Either URL or platform must be provided")
        return None
    
    async def parse_url(self, url: str, platform: str = None) -> dict:
        """
        Parse the given URL using the appropriate parser
        
        Args:
            url (str): The URL to parse
            platform (str, optional): The platform to use for parsing
            
        Returns:
            dict: Parsed metadata
            
        Raises:
            ValueError: If no appropriate parser found or parsing fails
        """
        parser = self.get_parser(url, platform=platform)
        if not parser:
            raise ValueError(f"No parser found for platform: {platform or 'unknown'}")
        
        return await parser.parse_url(url)

# Create a singleton instance
parser_factory = ParserFactory() 