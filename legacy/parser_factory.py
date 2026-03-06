import logging
from typing import Optional, Dict
from .base_parser import BaseParser
from .parsers.youtube_parser import YouTubeParser
from .parsers.tiktok_parser import TikTokParser
from .parsers.instagram_parser import InstagramParser
from .parsers.facebook_parser import FacebookParser
from .models import Platform

logger = logging.getLogger(__name__)

class ParserFactory:
    """Factory class for creating social media parsers"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._parsers: Dict[str, BaseParser] = {}
            self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize all parsers"""
        try:
            self._parsers['youtube'] = YouTubeParser()
            logger.info("YouTube parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube parser: {e}")
            
        try:
            self._parsers['tiktok'] = TikTokParser()
            logger.info("TikTok parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TikTok parser: {e}")
            
        try:
            self._parsers['instagram'] = InstagramParser()
            logger.info("Instagram parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram parser: {e}")
            
        try:
            self._parsers['facebook'] = FacebookParser()
            logger.info("Facebook parser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook parser: {e}")
    
    def get_parser(self, url: str = None, platform: str = None) -> Optional[BaseParser]:
        """
        Get appropriate parser for the given URL or platform
        
        Args:
            url (str, optional): The URL to parse
            platform (str, optional): The platform name
            
        Returns:
            Optional[BaseParser]: Appropriate parser instance or None if no parser found
        """
        if platform:
            platform = platform.lower()
            if platform in self._parsers:
                return self._parsers[platform]
            logger.error(f"No parser found for platform: {platform}")
            return None
            
        if url:
            url = url.lower()
            if 'youtube.com' in url or 'youtu.be' in url:
                return self._parsers.get('youtube')
            elif 'tiktok.com' in url:
                return self._parsers.get('tiktok')
            elif 'instagram.com' in url:
                return self._parsers.get('instagram')
            elif 'facebook.com' in url or 'fb.watch' in url:
                return self._parsers.get('facebook')
            logger.error(f"No parser found for URL: {url}")
            return None
            
        logger.error("Either URL or platform must be provided")
        return None
    
    async def parse_url(self, url: str) -> dict:
        """
        Parse the given URL using the appropriate parser
        
        Args:
            url (str): The URL to parse
            
        Returns:
            dict: Parsed metadata
            
        Raises:
            ValueError: If no appropriate parser found or parsing fails
        """
        parser = self.get_parser(url=url)
        if not parser:
            raise ValueError(f"Unsupported URL: {url}")
            
        try:
            return await parser.parse_url(url)
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            raise ValueError(f"Failed to parse URL: {str(e)}")
            
    async def cleanup(self):
        """Cleanup all parsers"""
        for parser in self._parsers.values():
            try:
                if hasattr(parser, '_close_session'):
                    await parser._close_session()
            except Exception as e:
                logger.error(f"Error cleaning up parser {parser.__class__.__name__}: {e}")

# Singleton instance
parser_factory = ParserFactory()

def get_parser(platform: str):
    """Factory function to get the appropriate parser for a platform"""
    if platform == Platform.youtube:
        return YouTubeParser()
    elif platform == Platform.tiktok:
        return TikTokParser()
    elif platform == Platform.instagram:
        return InstagramParser()
    else:
        raise ValueError(f"Unsupported platform: {platform}") 