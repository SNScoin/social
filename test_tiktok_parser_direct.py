import asyncio
import os
from dotenv import load_dotenv
import sys

# Add the backend/app directory to the Python path
sys.path.insert(0, 'backend/app')

load_dotenv()

async def test_tiktok_parser():
    print("Testing TikTok Parser directly...")
    
    # Check if APIFY_TOKEN is set
    apify_token = os.getenv('APIFY_TOKEN')
    print(f"APIFY_TOKEN set: {'Yes' if apify_token else 'No'}")
    if apify_token:
        print(f"Token length: {len(apify_token)} characters")
    
    try:
        from parsers.tiktok_parser import TikTokParser
        
        # Create parser instance
        parser = TikTokParser()
        print("✓ TikTokParser created successfully")
        
        # Test URL
        test_url = "https://www.tiktok.com/@kabooke12/video/7457851293294447878"
        print(f"Testing URL: {test_url}")
        
        # Validate URL
        is_valid = parser.validate_url(test_url)
        print(f"URL valid: {is_valid}")
        
        if is_valid:
            # Try to parse
            print("Attempting to parse...")
            result = await parser.parse_url(test_url)
            print(f"✓ Parse successful!")
            print(f"Title: {result.get('title')}")
            print(f"Views: {result.get('views')}")
            print(f"Likes: {result.get('likes')}")
            print(f"Comments: {result.get('comments')}")
        else:
            print("✗ URL validation failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tiktok_parser()) 