import re
import aiohttp
import os
from typing import Dict, Any, Optional
from .base_parser import BaseParser
import logging
from dotenv import load_dotenv
import asyncio
import json
import emoji

logger = logging.getLogger(__name__)

class TikTokParser(BaseParser):
    """Parser for TikTok videos using Apify Actor."""

    def __init__(self):
        super().__init__()
        self.platform = 'tiktok'
        load_dotenv()
        self.apify_token = os.getenv('APIFY_TOKEN')
        if not self.apify_token:
            raise ValueError("APIFY_TOKEN environment variable is not set")
        
        self.actor_id = "S5h7zRLfKFEr8pdj7"
        self.api_url = f"https://api.apify.com/v2/acts/{self.actor_id}/runs?token={self.apify_token}"
        self.session = None
        self._session_lock = asyncio.Lock()

    async def _init_session(self):
        async with self._session_lock:
            if not self.session:
                timeout = aiohttp.ClientTimeout(total=60)
                self.session = aiohttp.ClientSession(timeout=timeout)

    async def _close_session(self):
        async with self._session_lock:
            if self.session:
                await self.session.close()
                self.session = None

    def _extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'video/(\d+)',
            r'v/(\d+)',
            r'@[\w.-]+/video/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
            r'tiktok\.com/t/(\w+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def validate_url(self, url: str) -> bool:
        patterns = [
            r'https?://(?:www\.)?tiktok\.com/(@[\w.-]+/video/\d+)',
            r'https?://(?:www\.)?tiktok\.com/v/\d+',
            r'https?://(?:www\.)?vm\.tiktok\.com/\w+',
            r'https?://(?:www\.)?tiktok\.com/t/\w+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)

    def _clean_title(self, text: str, max_length: int = 100) -> str:
        if not text:
            return "Untitled TikTok Video"
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = emoji.replace_emoji(text, replace='')
        text = re.sub(r'[^\w\s#@.,!?-]', '', text)
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length - 3] + '...'
        return text or "Untitled TikTok Video"

    def _get_from_dot(self, data, *keys, default=None):
        for key in keys:
            if key in data:
                return data[key]
        return default

    async def _get_tiktok_data(self, url: str) -> Dict[str, Any]:
        await self._init_session()
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            input_data = {
                "postURLs": [url],
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
                "shouldDownloadSubtitles": False,
                "shouldDownloadSlideshowImages": False,
                "maxRequestRetries": 3,
                "maxConcurrency": 2,
                "proxyConfiguration": {
                    "useApifyProxy": True
                },
                "sessionPool": {
                    "maxPoolSize": 2,
                    "sessionOptions": {
                        "maxUsageCount": 2
                    }
                }
            }
            
            logger.info(f"Triggering Apify run for: {url}")
            async with self.session.post(self.api_url, headers=headers, json=input_data) as resp:
                if resp.status != 201:
                    raise ValueError(f"Failed to start Apify run: HTTP {resp.status}")
                run_data = await resp.json()
                run_id = run_data.get("data", {}).get("id")
                if not run_id:
                    raise ValueError("No run ID received")

            # Poll for completion
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_token}"
            max_attempts = 15
            for attempt in range(max_attempts):
                await asyncio.sleep(min(10, 1.2 ** attempt))
                async with self.session.get(status_url) as status_resp:
                    status_data = await status_resp.json()
                    status = status_data.get("data", {}).get("status")
                    if status == "SUCCEEDED":
                        break
                    elif status in ["FAILED", "ABORTED", "TIMEOUT"]:
                        raise ValueError(f"Run failed with status: {status}")
            else:
                raise TimeoutError("Apify run did not finish in time")
                
            # Fetch results
            dataset_id = status_data["data"].get("defaultDatasetId")
            if not dataset_id:
                raise ValueError("Dataset ID not found in run data")

            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_token}"
            for _ in range(5):
                await asyncio.sleep(2)
                async with self.session.get(dataset_url) as result_resp:
                    if result_resp.status != 200:
                        continue
                    results = await result_resp.json()
                    if results:
                        break
            else:
                raise ValueError("No data received from Apify dataset")
                    
            video_data = results[0]
            description = self._get_from_dot(video_data, 'text', 'desc', default='')
            hashtags = re.findall(r'#(\w+)', description)
            title = self._clean_title(description)
                    
            return {
                'title': title,
                'description': description,
                'views': self._get_from_dot(video_data, 'playCount', 'stats.playCount', default=0),
                'likes': self._get_from_dot(video_data, 'likesCount', 'diggCount', 'stats.diggCount', default=0),
                'comments': self._get_from_dot(video_data, 'commentsCount', 'commentCount', 'stats.commentCount', default=0),
                'owner': self._get_from_dot(video_data, 'authorMeta.name', 'author.nickname', default=''),
                'created_time': self._get_from_dot(video_data, 'createTime', 'createTimeISO', default=''),
                'hashtags': hashtags,
                'platform': 'tiktok'
            }
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise ValueError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise ValueError(f"Error fetching TikTok data: {e}")
        finally:
            await self._close_session()

    async def parse_url(self, url: str) -> Dict[str, Any]:
        if not self.validate_url(url):
            raise ValueError("Invalid TikTok URL")
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract video ID from URL")
        return await self._get_tiktok_data(url) 