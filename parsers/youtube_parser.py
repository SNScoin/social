import re
from typing import Dict, Any, Optional
import logging
import json
from googleapiclient.discovery import build
import os
from base_parser import BaseParser

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
        self.api_key = "AIzaSyBJh8PvT1avBVd01qUIrONkL4mBFFJaW1o"
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _safe_int_conversion(self, value: Any, default: int = 0) -> int:
        """Safely convert a value to integer"""
        if isinstance(value, int):
            return value
        try:
            return int(str(value).replace(',', ''))
        except (ValueError, TypeError, AttributeError):
            return default

    async def parse_url(self, url: str) -> Optional[Dict]:
        """Parse YouTube URL and return video statistics"""
        print("\n" + "="*20 + " STARTING YOUTUBE PARSER " + "="*20)
        
        # Extract video ID
        video_id = self._extract_video_id(url)
        if not video_id:
            error_msg = "Invalid YouTube URL format"
            print(f"✗ {error_msg}")
            raise ValueError(error_msg)
            
        print(f"✓ Extracted video ID: {video_id}")
        
        try:
            # Request video data from the YouTube API
            print("Fetching data from YouTube API...")
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                video_data = response['items'][0]
                snippet = video_data.get('snippet', {})
                statistics = video_data.get('statistics', {})
                
                # Convert statistics to integers
                views = self._safe_int_conversion(statistics.get('viewCount', '0'))
                likes = self._safe_int_conversion(statistics.get('likeCount', '0'))
                comments = self._safe_int_conversion(statistics.get('commentCount', '0'))
                
                result = {
                    "title": snippet.get('title', ''),
                    "views": views,
                    "likes": likes,
                    "comments": comments
                }
                
                print("✓ Successfully parsed video data:")
                print(f"Title: {result['title']}")
                print(f"Views: {views:,}")
                print(f"Likes: {likes:,}")
                print(f"Comments: {comments:,}")
                
                return result
            else:
                error_msg = "No video data found - the video might be private or deleted"
                print(f"✗ {error_msg}")
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                error_msg = "YouTube API quota exceeded. Please try again later."
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                error_msg = "Invalid YouTube API key. Please check your API key configuration."
            print(f"✗ Error fetching YouTube data: {error_msg}")
            raise ValueError(error_msg)

    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a YouTube URL"""
        return bool(self._extract_video_id(url)) 