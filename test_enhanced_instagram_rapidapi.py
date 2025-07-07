#!/usr/bin/env python3
"""
Test script for enhanced Instagram parser with RapidAPI ScrapeNinja integration
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.instagram_parser_enhanced import InstagramParserEnhanced

async def test_enhanced_instagram_rapidapi():
    """Test the enhanced Instagram parser with RapidAPI ScrapeNinja"""
    
    # Test URL (the same Instagram reel from before)
    test_url = "https://www.instagram.com/reel/C8qQZQZQZQZ/"
    
    print("🧪 Testing Enhanced Instagram Parser with RapidAPI ScrapeNinja")
    print("=" * 60)
    print(f"Test URL: {test_url}")
    print()
    
    # Initialize the parser
    parser = InstagramParserEnhanced()
    
    try:
        print("📡 Fetching Instagram data...")
        print("   (This may take a few seconds)")
        print()
        
        # Parse the URL
        result = await parser.parse_url(test_url)
        
        print("✅ Parsing completed successfully!")
        print()
        print("📊 Results:")
        print("-" * 30)
        print(f"Platform: {result.get('platform', 'N/A')}")
        print(f"Owner: {result.get('owner', 'N/A')}")
        print(f"Title: {result.get('title', 'N/A')[:100]}...")
        print(f"Likes: {result.get('likes', 'N/A'):,}" if result.get('likes') else "Likes: N/A")
        print(f"Comments: {result.get('comments', 'N/A'):,}" if result.get('comments') else "Comments: N/A")
        print(f"Views: {result.get('views', 'N/A'):,}" if result.get('views') else "Views: N/A")
        print(f"Hashtags: {', '.join(result.get('hashtags', []))}")
        print(f"Created Time: {result.get('created_time', 'N/A')}")
        
        if 'note' in result:
            print(f"Note: {result['note']}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        print()
        print("🔍 API Configuration:")
        print("-" * 30)
        print(f"RapidAPI Key: {'✅ Set' if parser.rapidapi_key else '❌ Not set'}")
        print(f"Direct ScrapeNinja Key: {'✅ Set' if parser.scrapeninja_key else '❌ Not set'}")
        
        # Test with a real Instagram URL if available
        real_url = input("\n🔗 Enter a real Instagram URL to test (or press Enter to skip): ").strip()
        
        if real_url:
            print(f"\n📡 Testing with real URL: {real_url}")
            print("   (This may take a few seconds)")
            print()
            
            real_result = await parser.parse_url(real_url)
            
            print("✅ Real URL parsing completed!")
            print()
            print("📊 Real URL Results:")
            print("-" * 30)
            print(f"Platform: {real_result.get('platform', 'N/A')}")
            print(f"Owner: {real_result.get('owner', 'N/A')}")
            print(f"Title: {real_result.get('title', 'N/A')[:100]}...")
            print(f"Likes: {real_result.get('likes', 'N/A'):,}" if real_result.get('likes') else "Likes: N/A")
            print(f"Comments: {real_result.get('comments', 'N/A'):,}" if real_result.get('comments') else "Comments: N/A")
            print(f"Views: {real_result.get('views', 'N/A'):,}" if real_result.get('views') else "Views: N/A")
            print(f"Hashtags: {', '.join(real_result.get('hashtags', []))}")
            
            if 'note' in real_result:
                print(f"Note: {real_result['note']}")
            
            if 'error' in real_result:
                print(f"Error: {real_result['error']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_instagram_rapidapi()) 