import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.parsers.parser_factory import parser_factory

async def test_enhanced_instagram_parser():
    """Test the enhanced Instagram parser integration"""
    url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
    
    print("🚀 Testing Enhanced Instagram Parser Integration")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    try:
        # Test 1: Get parser by platform
        print("🔍 Test 1: Getting parser by platform 'instagram_enhanced'")
        parser = parser_factory.get_parser(platform='instagram_enhanced')
        if parser:
            print(f"✅ Successfully got parser: {parser.__class__.__name__}")
            print(f"✅ Platform: {parser.platform}")
        else:
            print("❌ Failed to get parser by platform")
            return
        
        # Test 2: Validate URL
        print("\n🔍 Test 2: Validating URL")
        is_valid = parser.validate_url(url)
        print(f"✅ URL validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print("❌ Invalid URL format")
            return
        
        # Test 3: Parse URL directly
        print("\n🔍 Test 3: Parsing URL directly")
        result = await parser.parse_url(url)
        
        print("\n📊 Parsing Results:")
        print("=" * 50)
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Views: {result.get('views', 'N/A'):,}" if result.get('views') else f"Views: {result.get('views', 'N/A')}")
        print(f"Likes: {result.get('likes', 'N/A'):,}" if result.get('likes') else f"Likes: {result.get('likes', 'N/A')}")
        print(f"Comments: {result.get('comments', 'N/A'):,}" if result.get('comments') else f"Comments: {result.get('comments', 'N/A')}")
        print(f"Owner: {result.get('owner', 'N/A')}")
        print(f"Platform: {result.get('platform', 'N/A')}")
        
        if 'note' in result:
            print(f"Note: {result['note']}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        
        # Test 4: Use parser factory to parse URL
        print("\n🔍 Test 4: Using parser factory to parse URL")
        factory_result = await parser_factory.parse_url(url, platform='instagram_enhanced')
        
        print("\n📊 Factory Results:")
        print("=" * 50)
        print(f"Title: {factory_result.get('title', 'N/A')}")
        print(f"Views: {factory_result.get('views', 'N/A'):,}" if factory_result.get('views') else f"Views: {factory_result.get('views', 'N/A')}")
        print(f"Likes: {factory_result.get('likes', 'N/A'):,}" if factory_result.get('likes') else f"Likes: {factory_result.get('likes', 'N/A')}")
        print(f"Comments: {factory_result.get('comments', 'N/A'):,}" if factory_result.get('comments') else f"Comments: {factory_result.get('comments', 'N/A')}")
        print(f"Owner: {factory_result.get('owner', 'N/A')}")
        print(f"Platform: {factory_result.get('platform', 'N/A')}")
        
        # Summary
        print("\n🎯 Summary:")
        if result.get('views'):
            print(f"✅ SUCCESS: Enhanced parser extracted view count: {result['views']:,}")
        else:
            print("❌ FAILED: No view count available")
        
        if result.get('likes') and result.get('comments'):
            print(f"✅ SUCCESS: Enhanced parser extracted engagement metrics")
        else:
            print("❌ FAILED: No engagement metrics available")
            
        # Compare with original parser
        print("\n🔍 Test 5: Comparing with original Instagram parser")
        try:
            original_parser = parser_factory.get_parser(platform='instagram')
            if original_parser:
                original_result = await original_parser.parse_url(url)
                print(f"Original parser views: {original_result.get('views', 'N/A')}")
                print(f"Enhanced parser views: {result.get('views', 'N/A')}")
                
                if result.get('views') and not original_result.get('views'):
                    print("✅ Enhanced parser provides view count while original doesn't!")
                elif result.get('views') and original_result.get('views'):
                    print("✅ Both parsers provide view counts")
                else:
                    print("⚠️ Neither parser provides view counts")
        except Exception as e:
            print(f"⚠️ Could not compare with original parser: {str(e)}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_instagram_parser()) 