import aiohttp
import json
import re
from typing import Optional, Dict, Any
import logging
from backend.app.parsers.youtube_parser import YouTubeParser
from backend.app.models.models import Platform
from backend.app.parsers.parser_factory import ParserFactory

logger = logging.getLogger(__name__)

parser_factory = ParserFactory()

async def parse_social_link(url: str) -> dict:
    """Parse social media link and return metrics"""
    logger.info(f"Parsing social link: {url}")
    parser = parser_factory.get_parser(url)
    if not parser:
        logger.error(f"No parser found for URL: {url}")
        raise ValueError("Unsupported URL")
    
    try:
        result = await parser.parse_url(url)
        logger.info(f"Successfully parsed URL: {url}")
        return result
    except Exception as e:
        logger.error(f"Error parsing URL {url}: {str(e)}")
        raise

async def parse_instagram(url: str) -> Dict[str, Any]:
    """Parse Instagram post/reel metrics"""
    # Extract post ID from URL
    match = re.search(r'instagram\.com\/(?:p|reel)\/([^\/\?]+)', url)
    if not match:
        raise ValueError("Invalid Instagram URL")
    
    post_id = match.group(1)
    
    # For demo purposes, return dummy data
    # In production, you would use Instagram's API
    return {
        'title': f'Instagram Post {post_id}',
        'views': 1000,
        'likes': 500,
        'comments': 50
    }

async def parse_tiktok(url: str) -> Dict[str, Any]:
    """Parse TikTok video metrics"""
    # Extract video ID from URL
    match = re.search(r'tiktok\.com\/(?:@[^\/]+\/video\/|video\/)(\d+)', url)
    if not match:
        raise ValueError("Invalid TikTok URL")
    
    video_id = match.group(1)
    
    # For demo purposes, return dummy data
    # In production, you would use TikTok's API
    return {
        'title': f'TikTok Video {video_id}',
        'views': 5000,
        'likes': 2000,
        'comments': 100
    }

async def parse_youtube(url: str) -> Dict[str, Any]:
    """Parse YouTube video metrics"""
    # Extract video ID from URL
    patterns = [
        r'youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be\/([a-zA-Z0-9_-]+)',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]+)'
    ]
    
    video_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    # For demo purposes, return dummy data
    # In production, you would use YouTube's API
    return {
        'title': f'YouTube Video {video_id}',
        'views': 10000,
        'likes': 1000,
        'comments': 200
    } 