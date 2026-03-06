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

class InstagramParserEnhanced(BaseParser):
    """Enhanced Instagram parser with ScrapeNinja API and view count estimation"""
    
    def __init__(self):
        super().__init__()
        self.platform = 'instagram_enhanced'
        self.required_fields = ['likes', 'comments', 'views']
        load_dotenv()
        
        # Support both direct ScrapeNinja and RapidAPI ScrapeNinja
        self.scrapeninja_key = os.getenv('SCRAPENINJA_API_KEY')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184')
        
        if not self.scrapeninja_key:
            logger.warning("SCRAPENINJA_API_KEY environment variable is not set")
        if not self.rapidapi_key:
            logger.warning("RAPIDAPI_KEY environment variable is not set")
        
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
        """Parse Instagram URL with enhanced view count handling"""
        if not self.validate_url(url):
            raise ValueError("Invalid Instagram URL format")
        
        try:
            # Try multiple parsing strategies
            metrics = await self._try_multiple_parsing_strategies(url)
            if not metrics:
                raise ValueError("Could not fetch post data from any source")
            
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
                "platform": "instagram_enhanced",
                "error": str(e)
            }
    
    async def _try_multiple_parsing_strategies(self, url: str) -> Dict[str, Any]:
        """Try multiple parsing strategies in order of preference"""
        
        # Strategy 1: Try ScrapeNinja via RapidAPI (most reliable)
        try:
            logger.info("Trying ScrapeNinja via RapidAPI...")
            metrics = await self._get_instagram_data_scrapeninja_rapidapi(url)
            if metrics and self._has_valid_metrics(metrics):
                logger.info("✅ ScrapeNinja via RapidAPI strategy successful")
                return metrics
        except Exception as e:
            logger.warning(f"ScrapeNinja via RapidAPI strategy failed: {str(e)}")
        
        # Strategy 2: Try direct ScrapeNinja API (if available)
        if self.scrapeninja_key:
            try:
                logger.info("Trying direct ScrapeNinja API...")
                metrics = await self._get_instagram_data_scrapeninja_direct(url)
                if metrics and self._has_valid_metrics(metrics):
                    logger.info("✅ Direct ScrapeNinja API strategy successful")
                    return metrics
            except Exception as e:
                logger.warning(f"Direct ScrapeNinja API strategy failed: {str(e)}")
        
        # Strategy 3: Fallback to estimated metrics
        logger.info("Using fallback strategy with estimated metrics...")
        return await self._get_fallback_metrics(url)
    
    def _has_valid_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Check if metrics contain valid data"""
        return (
            metrics.get('likes') is not None and metrics.get('likes') > 0 or
            metrics.get('comments') is not None and metrics.get('comments') > 0 or
            metrics.get('views') is not None and metrics.get('views') > 0
        )
    
    async def _get_instagram_data_scrapeninja_rapidapi(self, url: str) -> Dict[str, Any]:
        """Fetch Instagram data using ScrapeNinja via RapidAPI"""
        if not self.rapidapi_key:
            raise ValueError("RapidAPI key not available")
        
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://scrapeninja.p.rapidapi.com/scrape"
                
                headers = {
                    "x-rapidapi-key": self.rapidapi_key,
                    "x-rapidapi-host": "scrapeninja.p.rapidapi.com",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "url": url,
                    "render": True,
                    "wait": 3000
                }
                
                logger.info(f"Starting ScrapeNinja via RapidAPI request for URL: {url}")
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ScrapeNinja via RapidAPI request failed: HTTP {response.status}, {error_text}")
                        raise ValueError(f"ScrapeNinja via RapidAPI failed: HTTP {response.status}")
                    
                    result = await response.json()
                    logger.info(f"ScrapeNinja via RapidAPI response received")
                    
                    if 'body' not in result:
                        logger.error("No HTML body in ScrapeNinja via RapidAPI response")
                        raise ValueError("No HTML content received")
                    
                    html_content = result['body']
                    return self._parse_instagram_html(html_content, url)
                    
        except Exception as e:
            logger.error(f"ScrapeNinja via RapidAPI error: {str(e)}")
            raise
    
    async def _get_instagram_data_scrapeninja_direct(self, url: str) -> Dict[str, Any]:
        """Fetch Instagram data using direct ScrapeNinja API"""
        if not self.scrapeninja_key:
            raise ValueError("Direct ScrapeNinja API key not available")
        
        try:
            async with aiohttp.ClientSession() as session:
                api_url = "https://api.scrapeninja.com/v1/scrape"
                
                headers = {
                    "Authorization": f"Bearer {self.scrapeninja_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "url": url,
                    "render": True,
                    "wait": 3000
                }
                
                logger.info(f"Starting direct ScrapeNinja request for URL: {url}")
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Direct ScrapeNinja request failed: HTTP {response.status}, {error_text}")
                        raise ValueError(f"Direct ScrapeNinja failed: HTTP {response.status}")
                    
                    result = await response.json()
                    
                    if 'body' not in result:
                        logger.error("No HTML body in direct ScrapeNinja response")
                        raise ValueError("No HTML content received")
                    
                    html_content = result['body']
                    return self._parse_instagram_html(html_content, url)
                    
        except Exception as e:
            logger.error(f"Direct ScrapeNinja error: {str(e)}")
            raise
    
    def _parse_instagram_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse Instagram HTML content to extract metrics"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract post ID
            post_id = self._extract_post_id(url)
            
            # Extract metrics from meta description
            description_pattern = r'content="([^"]*likes[^"]*comments[^"]*)"'
            description_matches = re.findall(description_pattern, html_content)
            
            metrics = {
                'title': '',
                'views': None,
                'likes': 0,
                'comments': 0,
                'owner': 'Unknown',
                'created_time': '',
                'hashtags': [],
                'platform': 'instagram_enhanced'
            }
            
            if description_matches:
                description = description_matches[0]
                logger.info(f"Found description: {description}")
                
                # Extract likes and comments
                likes_pattern = r'(\d+(?:,\d+)*)\s*likes'
                comments_pattern = r'(\d+(?:,\d+)*)\s*comments'
                
                likes_match = re.search(likes_pattern, description)
                comments_match = re.search(comments_pattern, description)
                
                if likes_match:
                    metrics['likes'] = int(likes_match.group(1).replace(',', ''))
                    logger.info(f"Extracted likes: {metrics['likes']:,}")
                if comments_match:
                    metrics['comments'] = int(comments_match.group(1).replace(',', ''))
                    logger.info(f"Extracted comments: {metrics['comments']:,}")
                
                # Extract username
                username_pattern = r'-\s*([^:]+?)\s+on\s+'
                username_match = re.search(username_pattern, description)
                if username_match:
                    metrics['owner'] = username_match.group(1).strip()
                    logger.info(f"Extracted username: {metrics['owner']}")
                else:
                    # Fallback pattern
                    username_pattern = r'-\s*([^:]+):'
                    username_match = re.search(username_pattern, description)
                    if username_match:
                        metrics['owner'] = username_match.group(1).strip()
                        logger.info(f"Extracted username: {metrics['owner']}")
                
                # Extract caption
                caption_pattern = r':\s*"([^"]+)"'
                caption_match = re.search(caption_pattern, description)
                if caption_match:
                    metrics['title'] = caption_match.group(1)
                    metrics['hashtags'] = re.findall(r'#(\w+)', caption_match.group(1))
                    logger.info(f"Extracted caption: {metrics['title'][:50]}...")
            
            # Try to extract view count from JSON data in HTML
            view_count = self._extract_view_count_from_json(html_content, post_id)
            if view_count is not None:
                metrics['views'] = view_count
                logger.info(f"Extracted view count: {view_count:,}")
            else:
                logger.info("No view count found in JSON data")
            
            # If no view count found, estimate based on engagement
            if metrics['views'] is None and metrics['likes'] > 0:
                metrics['views'] = self._estimate_views_from_engagement(metrics['likes'], metrics['comments'])
                logger.info(f"Estimated view count: {metrics['views']:,}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            raise
    
    def _extract_view_count_from_json(self, html_content: str, post_id: str) -> Optional[int]:
        """Extract view count from JSON data in HTML"""
        try:
            # Look for the specific post data in JSON
            post_pattern = rf'"shortcode":"{post_id}".*?"view_count":(\d+|null)'
            match = re.search(post_pattern, html_content, re.DOTALL)
            
            if match:
                view_count_str = match.group(1)
                if view_count_str != 'null':
                    return int(view_count_str)
            
            # Look for any view count data
            view_count_pattern = r'"view_count":(\d+)'
            matches = re.findall(view_count_pattern, html_content)
            
            if matches:
                # Return the first non-zero view count
                for match in matches:
                    view_count = int(match)
                    if view_count > 0:
                        return view_count
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting view count from JSON: {str(e)}")
            return None
    
    def _estimate_views_from_engagement(self, likes: int, comments: int) -> int:
        """Estimate views based on engagement metrics"""
        try:
            # Instagram typically has 1-5% engagement rate
            # Use a conservative estimate of 2% engagement rate
            engagement_rate = 0.02
            
            # Calculate estimated views based on likes and comments
            total_engagement = likes + comments
            estimated_views = int(total_engagement / engagement_rate)
            
            # Ensure reasonable bounds (minimum 1000, maximum 10M)
            estimated_views = max(1000, min(estimated_views, 10000000))
            
            logger.info(f"Engagement analysis:")
            logger.info(f"  Total engagement: {total_engagement:,}")
            logger.info(f"  Engagement rate: {engagement_rate:.1%}")
            logger.info(f"  Estimated views: {estimated_views:,}")
            
            return estimated_views
            
        except Exception as e:
            logger.warning(f"Error estimating views: {str(e)}")
            return 1000  # Default fallback
    
    async def _get_fallback_metrics(self, url: str) -> Dict[str, Any]:
        """Get fallback metrics when all other strategies fail"""
        post_id = self._extract_post_id(url)
        
        return {
            'title': f'Instagram Post {post_id}',
            'views': 1000,  # Conservative estimate
            'likes': 100,   # Conservative estimate
            'comments': 10, # Conservative estimate
            'owner': 'Unknown',
            'created_time': '',
            'hashtags': [],
            'platform': 'instagram_enhanced',
            'note': 'Fallback data - actual metrics unavailable'
        }
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        """Extract post ID from Instagram URL"""
        try:
            if '/p/' in url:
                post_id = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                post_id = url.split('/reel/')[1].split('/')[0]
            else:
                return None
            
            return post_id
        except Exception:
            return None 