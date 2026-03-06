import requests
import json
import re
from typing import Dict, Any, Optional
from .base_parser import BaseParser
import logging
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FacebookParser(BaseParser):
    """Parser for Facebook Reels"""
    
    def __init__(self):
        """Initialize the Facebook parser"""
        super().__init__()
        self.platform = "facebook"
        # Try to get API key from environment, fallback to hardcoded key
        self.api_key = os.getenv("FACEBOOK_RAPIDAPI_KEY", "686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184")
        self.api_host = "facebook-scraper3.p.rapidapi.com"
        self.api_url = f"https://{self.api_host}/post"
        logger.info(f"[FACEBOOK_PARSER] Initialized with API key: {self.api_key[:10]}...")
        
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a Facebook URL"""
        facebook_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/reel\/\d+',
            r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/.*\/videos\/\d+',
            r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/watch\/\?v=\d+'
        ]
        return any(re.match(pattern, url) for pattern in facebook_patterns)
    
    def can_handle(self, url: str) -> bool:
        """Check if the URL is a Facebook URL"""
        return self.validate_url(url)
    
    def extract_id(self, url: str) -> Optional[str]:
        """Extract the Facebook video/reel ID from the URL"""
        patterns = [
            r'facebook\.com\/reel\/(\d+)',
            r'facebook\.com\/.*\/videos\/(\d+)',
            r'facebook\.com\/watch\/\?v=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_metrics(self, url: str) -> Dict[str, Any]:
        """Get metrics for a Facebook video/reel using RapidAPI"""
        try:
            logger.info(f"[FACEBOOK_PARSER] Getting metrics for URL: {url}")
            video_id = self.extract_id(url)
            logger.info(f"[FACEBOOK_PARSER] Extracted video ID: {video_id}")
            if not video_id:
                raise ValueError(f"Could not extract video ID from URL: {url}")
            
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.api_host
            }
            params = {"post_id": video_id}
            
            # Make async API call
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, headers=headers, params=params) as response:
                    logger.info(f"[FACEBOOK_PARSER] Response status code: {response.status}")
                    response_text = await response.text()
                    logger.info(f"[FACEBOOK_PARSER] Raw response: {response_text}")
            
                    if response.status != 200:
                        error_text = response_text
                        logger.error(f"[FACEBOOK_PARSER] API error: {error_text}")
                        raise ValueError(f"API error: {error_text}")
                    
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"[FACEBOOK_PARSER] Invalid JSON response: {str(e)}")
                        raise ValueError(f"Invalid JSON response: {str(e)}")
                    
                    logger.info(f"[FACEBOOK_PARSER] Parsed JSON data: {data}")
            
            # Extract metrics from the API response
            results = data.get('results', {})
            
            # Parse play count from text (e.g., "5.3M")
            play_count_text = results.get('play_count_text', '')
            play_count = None
            if play_count_text:
                try:
                    if 'M' in play_count_text:
                        play_count = int(float(play_count_text.replace('M', '')) * 1_000_000)
                    elif 'K' in play_count_text:
                        play_count = int(float(play_count_text.replace('K', '')) * 1_000)
                    else:
                        play_count = int(play_count_text)
                except (ValueError, TypeError):
                    logger.warning(f"[FACEBOOK_PARSER] Could not parse play count: {play_count_text}")
            
            # Get other metrics
            metrics = {
                "title": results.get('description', f"Facebook Video {video_id}"),
                "views": play_count,  # Using play_count as views
                "video_play_count": play_count,
                "likes": results.get('reactions_count'),
                "comments": results.get('comments_count'),
                "shares": results.get('reshare_count'),
                "owner": results.get('author', {}).get('name'),
                "created_time": results.get('timestamp'),
                "hashtags": [tag.strip("#") for tag in re.findall(r'#\w+', results.get('description', ""))],
                "platform": "facebook"
            }
            
            # Log the extracted metrics
            logger.info(f"[FACEBOOK_PARSER] Extracted metrics: {metrics}")
            
            # Validate metrics
            if not any([metrics['views'], metrics['likes'], metrics['comments']]):
                logger.warning("[FACEBOOK_PARSER] No metrics found in response")
                metrics['error'] = "No metrics found in response"
            
            return metrics
            
        except aiohttp.ClientError as e:
            logger.error(f"[FACEBOOK_PARSER] Network error: {str(e)}")
            raise ValueError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"[FACEBOOK_PARSER] Invalid JSON response: {str(e)}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"[FACEBOOK_PARSER] Error getting Facebook metrics: {str(e)}")
            return {
                "title": "Unknown Facebook Video",
                "views": None,
                "video_play_count": None,
                "likes": None,
                "comments": None,
                "shares": None,
                "error": str(e)
            }
    
    async def parse_url(self, url: str) -> Dict[str, Any]:
        """Parse Facebook URL and return video statistics"""
        try:
            if not self.validate_url(url):
                raise ValueError(f"Invalid Facebook URL: {url}")
            
            video_id = self.extract_id(url)
            if not video_id:
                raise ValueError(f"Could not extract video ID from URL: {url}")
            
            # Get metrics using RapidAPI
            metrics = await self.get_metrics(url)
            
            return {
                "title": metrics.get("title", f"Facebook Video {video_id}"),
                "views": metrics.get("views"),
                "likes": metrics.get("likes"),
                "comments": metrics.get("comments"),
                "shares": metrics.get("shares"),
                "owner": metrics.get("owner"),
                "created_time": metrics.get("created_time"),
                "hashtags": metrics.get("hashtags", []),
                "platform": "facebook",
                "video_play_count": metrics.get("video_play_count"),
                "error": metrics.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error parsing Facebook URL: {str(e)}")
            return {
                "title": "Unknown Facebook Video",
                "views": None,
                "likes": None,
                "comments": None,
                "shares": None,
                "platform": "facebook",
                "error": str(e)
            } 