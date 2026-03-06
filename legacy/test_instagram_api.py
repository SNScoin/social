import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_instagram_link():
    """Test adding the Instagram link through the API"""
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
        
        # Add the Instagram link
        headers = {'Authorization': f'Bearer {token}'}
        link_data = {
            'url': 'https://www.instagram.com/p/DJTxMx6NAUq',
            'company_id': 8
        }
        
        logger.info("Adding Instagram link through API...")
        async with session.post('http://localhost:8000/api/links/', 
                               json=link_data, headers=headers) as resp:
            if resp.status != 200:
                logger.error(f"Add link failed: {resp.status}")
                error_text = await resp.text()
                logger.error(f"Error: {error_text}")
                return None
            
            result = await resp.json()
            logger.info(f"API Response: {json.dumps(result, indent=2)}")
            
            title = result.get('title', 'NO TITLE')
            platform = result.get('platform')
            link_id = result.get('id')
            
            logger.info(f"Title: '{title}'")
            logger.info(f"Platform: {platform}")
            logger.info(f"Link ID: {link_id}")
            
            if title and title != 'NO TITLE' and title.strip():
                logger.info("✅ SUCCESS: Title extracted successfully through API")
            else:
                logger.warning("⚠️  WARNING: No title extracted through API")
            
            return result

if __name__ == "__main__":
    asyncio.run(test_instagram_link()) 