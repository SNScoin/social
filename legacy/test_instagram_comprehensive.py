import asyncio
import sys
import os
import time

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.instagram_parser import InstagramParser
from utils.social_parser import parse_instagram

async def test_instagram_parsers():
    """Test multiple Instagram parsing approaches"""
    url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
    
    print(f"Testing Instagram parsers with URL: {url}")
    print("=" * 70)
    
    # Test 1: Main Instagram Parser (RapidAPI)
    print("\n🔍 TEST 1: Main Instagram Parser (RapidAPI)")
    print("-" * 50)
    try:
        parser = InstagramParser()
        print("✓ Parser initialized")
        
        is_valid = parser.validate_url(url)
        print(f"✓ URL validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if is_valid:
            print("🔄 Attempting to parse with RapidAPI...")
            result = await parser.parse_url(url)
            
            print("\n📊 Results:")
            print(f"Title: {result.get('title', 'N/A')[:100]}...")
            print(f"Views: {result.get('views', 'N/A')}")
            print(f"Likes: {result.get('likes', 'N/A')}")
            print(f"Comments: {result.get('comments', 'N/A')}")
            print(f"Owner: {result.get('owner', 'N/A')}")
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Success!")
                
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
    
    # Wait a bit before next test
    print("\n⏳ Waiting 2 seconds before next test...")
    await asyncio.sleep(2)
    
    # Test 2: Fallback Instagram Parser
    print("\n🔍 TEST 2: Fallback Instagram Parser")
    print("-" * 50)
    try:
        print("🔄 Attempting to parse with fallback parser...")
        result = await parse_instagram(url)
        
        print("\n📊 Results:")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Views: {result.get('views', 'N/A')}")
        print(f"Likes: {result.get('likes', 'N/A')}")
        print(f"Comments: {result.get('comments', 'N/A')}")
        print("✅ Fallback parser worked!")
        
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
    
    # Test 3: URL Analysis
    print("\n🔍 TEST 3: URL Analysis")
    print("-" * 50)
    try:
        # Extract post ID manually
        import re
        match = re.search(r'instagram\.com\/reel\/([^\/\?]+)', url)
        if match:
            post_id = match.group(1)
            print(f"✓ Post ID extracted: {post_id}")
            print(f"✓ URL type: Instagram Reel")
            print(f"✓ Clean URL: https://www.instagram.com/reel/{post_id}/")
        else:
            print("❌ Could not extract post ID")
            
    except Exception as e:
        print(f"❌ Test 3 failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_instagram_parsers()) 