import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_add_link(url, company_id=8):
    """Test adding a link and check if title is returned"""
    async with aiohttp.ClientSession() as session:
        # Login first
        login_data = {
            'username': 'test@example.com',
            'password': 'testpassword123'
        }
        
        async with session.post('http://localhost:8000/token', data=login_data) as resp:
            if resp.status != 200:
                logger.error(f"Login failed: {resp.status}")
                return None
            token_data = await resp.json()
            token = token_data['access_token']
        
        # Add the link
        headers = {'Authorization': f'Bearer {token}'}
        link_data = {
            'url': url,
            'company_id': company_id
        }
        
        logger.info(f"Adding link: {url}")
        async with session.post('http://localhost:8000/api/links/', 
                               json=link_data, headers=headers) as resp:
            if resp.status != 200:
                logger.error(f"Add link failed: {resp.status}")
                error_text = await resp.text()
                logger.error(f"Error: {error_text}")
                return None
            
            result = await resp.json()
            logger.info(f"Success! Title: '{result.get('title', 'NO TITLE')}'")
            logger.info(f"Platform: {result.get('platform')}")
            logger.info(f"Link ID: {result.get('id')}")
            return result

async def main():
    """Test all platforms"""
    test_urls = [
        # YouTube
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        # TikTok  
        "https://www.tiktok.com/@tiktok/video/7232187813978351878",
        # Instagram
        "https://www.instagram.com/p/C4qXqXqXqXq/",
        # Facebook (already tested)
        "https://www.facebook.com/reel/1016000563989440"
    ]
    
    logger.info("Testing title parsing for all platforms...")
    
    for url in test_urls:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {url}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_add_link(url)
            if result:
                title = result.get('title', 'NO TITLE')
                if title and title != 'NO TITLE':
                    logger.info(f"✅ SUCCESS: Title extracted: '{title}'")
                else:
                    logger.warning(f"⚠️  WARNING: No title extracted")
            else:
                logger.error(f"❌ FAILED: Could not add link")
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
        
        # Wait a bit between requests
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main()) 