import re
import os
import logging
from typing import Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from .base_parser import BaseParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_separator():
    """Print a separator line"""
    print("\n" + "="*50)

def log_step(step: str, data: Any = None):
    """Helper function to log each step with clear separation"""
    print_separator()
    print(f"[STEP] {step}")
    if data:
        print(data)
    print_separator()

class YouTubeParser(BaseParser):
    """Parser for YouTube URLs"""
    
    def __init__(self):
        """Initialize the YouTube parser with API credentials"""
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is not set")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            logger.info("YouTube API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {str(e)}")
            raise

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.debug(f"Extracted video ID: {video_id}")
                return video_id
        
        logger.warning(f"Could not extract video ID from URL: {url}")
        return None

    def _safe_int_conversion(self, value: Any, default: int = 0) -> int:
        """Safely convert a value to integer"""
        if isinstance(value, int):
            return value
        try:
            return int(str(value).replace(',', ''))
        except (ValueError, TypeError, AttributeError):
            logger.warning(f"Failed to convert value to integer: {value}")
            return default

    async def parse_url(self, url: str) -> Optional[Dict]:
        """Parse YouTube URL and return video statistics"""
        logger.info(f"Starting to parse YouTube URL: {url}")
        
        # Extract video ID
        video_id = self._extract_video_id(url)
        if not video_id:
            error_msg = "Invalid YouTube URL format"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info(f"Successfully extracted video ID: {video_id}")
        
        try:
            # Request video data from the YouTube API
            logger.info("Fetching data from YouTube API...")
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                error_msg = "No video data found - the video might be private or deleted"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            video_data = response['items'][0]
            snippet = video_data.get('snippet', {})
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            
            # Convert statistics to integers
            views = self._safe_int_conversion(statistics.get('viewCount', '0'))
            likes = self._safe_int_conversion(statistics.get('likeCount', '0'))
            comments = self._safe_int_conversion(statistics.get('commentCount', '0'))
            
            # Check if video is available
            if content_details.get('uploadStatus') != 'processed':
                logger.warning("Video is not fully processed yet")
            
            result = {
                "title": snippet.get('title', ''),
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration": content_details.get('duration', ''),
                "published_at": snippet.get('publishedAt', '')
            }
            
            logger.info("Successfully parsed video data:")
            logger.info(f"Title: {result['title']}")
            logger.info(f"Views: {views:,}")
            logger.info(f"Likes: {likes:,}")
            logger.info(f"Comments: {comments:,}")
            
            return result
                
        except HttpError as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                error_msg = "YouTube API quota exceeded. Please try again later."
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                error_msg = "Invalid YouTube API key. Please check your API key configuration."
            logger.error(f"HTTP Error fetching YouTube data: {error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error fetching YouTube data: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a YouTube URL"""
        # First check if it's a YouTube URL
        youtube_domains = ['youtube.com', 'youtu.be', 'youtube.be']
        if not any(domain in url.lower() for domain in youtube_domains):
            return False
        # Then try to extract video ID
        return bool(self._extract_video_id(url)) 