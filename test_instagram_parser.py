import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.instagram_parser import InstagramParser

async def test_instagram_parser():
    """Test the Instagram parser with the provided URL"""
    url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
    
    print(f"Testing Instagram parser with URL: {url}")
    print("=" * 60)
    
    try:
        # Initialize the parser
        parser = InstagramParser()
        print("✓ Instagram parser initialized successfully")
        
        # Validate the URL
        is_valid = parser.validate_url(url)
        print(f"✓ URL validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print("❌ URL validation failed, stopping test")
            return
        
        # Parse the URL
        print("🔄 Parsing Instagram URL...")
        result = await parser.parse_url(url)
        
        print("\n📊 Parsing Results:")
        print("-" * 30)
        print(f"Title: {result.get('title', 'N/A')[:100]}...")
        print(f"Views: {result.get('views', 'N/A')}")
        print(f"Likes: {result.get('likes', 'N/A')}")
        print(f"Comments: {result.get('comments', 'N/A')}")
        print(f"Owner: {result.get('owner', 'N/A')}")
        print(f"Created Time: {result.get('created_time', 'N/A')}")
        print(f"Hashtags: {result.get('hashtags', [])}")
        print(f"Platform: {result.get('platform', 'N/A')}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Parsing completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 