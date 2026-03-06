from .base_parser import BaseParser
import re
import json
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramParser(BaseParser):
    """Parser for Instagram links"""
    
    def __init__(self):
        super().__init__()
        self.platform = 'instagram'
        self.required_fields = ['likes', 'comments', 'views']
        load_dotenv()
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        
        if not self.rapidapi_key:
            raise ValueError("RAPIDAPI_KEY environment variable is not set")
        
    def validate_url(self, url: str) -> bool:
        """Validate Instagram URL format"""
        try:
            result = urlparse(url)
            return all([
                result.scheme in ['http', 'https'],
                'instagram.com' in result.netloc,
                result.path.strip('/')
            ])
        except Exception:
            return False
    
    async def parse_url(self, url: str) -> Dict[str, Any]:
        """Parse Instagram URL and return stats"""
        if not self.validate_url(url):
            raise ValueError("Invalid Instagram URL format")
        
        try:
            # Get post data from Instagram API
            metrics = await self._get_instagram_data(url)
            if not metrics:
                raise ValueError("Could not fetch post data")
            
            return metrics
        except Exception as e:
            logger.error(f"Error parsing Instagram URL: {str(e)}")
            return {
                "title": "",
                "views": None,
                "likes": None,
                "comments": None,
                "owner": None,
                "created_time": None,
                "hashtags": [],
                "platform": "instagram",
                "error": str(e)
            }
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        """Extract post ID from Instagram URL"""
        try:
            # Handle different URL formats
            if '/p/' in url:
                # Standard post URL
                post_id = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                # Reel URL
                post_id = url.split('/reel/')[1].split('/')[0]
            else:
                return None
            
            return post_id
        except Exception:
            return None
    
    def _format_number(self, text: str) -> int:
        """Convert number with K, M, B suffixes to integer"""
        if not text or not isinstance(text, str):
            return 0
            
        text = text.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        try:
            for suffix, multiplier in multipliers.items():
                if text.endswith(suffix):
                    number = float(text[:-1].replace(',', ''))
                    return int(number * multiplier)
            return int(float(text.replace(',', '')))
        except (ValueError, TypeError):
            return 0
    
    async def _get_instagram_data(self, url: str) -> dict:
        """Fetch Instagram post data using RapidAPI"""
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/media_info"
                
                headers = {
                    "x-rapidapi-key": self.rapidapi_key,
                    "x-rapidapi-host": "real-time-instagram-scraper-api1.p.rapidapi.com"
                }
                
                params = {
                    "code_or_id_or_url": url
                }
                
                logger.info(f"Starting RapidAPI scraper for URL: {url}")
                async with session.get(api_url, params=params, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed: HTTP {response.status}, {error_text}")
                        raise ValueError(f"Failed to fetch data: HTTP {response.status}, {error_text}")
                    
                    result = await response.json()
                    logger.debug(f"Raw response data: {json.dumps(result, indent=2)}")
                    
                    if result.get('status') != 'ok':
                        error_msg = result.get('message', 'Unknown error')
                        logger.error(f"API returned error: {error_msg}")
                        raise ValueError(f"API returned error: {error_msg}")
                    
                    # Extract data from the first item in the response
                    items = result.get('data', {}).get('items', [])
                    if not items:
                        logger.error("No items found in API response")
                        raise ValueError("No post data found in API response")
                    
                    item = items[0]
                    caption = item.get('caption', {})
                    
                    metrics = {
                        'title': caption.get('text', ''),
                        'views': item.get('play_count', 0),
                        'likes': item.get('like_count', 0),
                        'comments': item.get('comment_count', 0),
                        'owner': item.get('user', {}).get('username', ''),
                        'created_time': item.get('taken_at', ''),
                        'hashtags': re.findall(r'#(\w+)', caption.get('text', '')),
                        'platform': 'instagram'
                    }
                    
                    logger.info(f"Successfully extracted metrics: {metrics}")
                    return metrics

        except aiohttp.ClientError as e:
            logger.error(f"Network error during RapidAPI request: {str(e)}")
            raise ValueError(f"Failed to fetch Instagram post: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError("Failed to parse API response")
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            raise ValueError(f"Error fetching Instagram data: {str(e)}")