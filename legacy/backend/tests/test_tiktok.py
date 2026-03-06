import asyncio
import traceback
from backend.app.parsers.tiktok_parser import TikTokParser

async def main():
    # Test URL - using a different TikTok video
    test_url = "https://www.tiktok.com/@tiktok/video/7321803408461325614"
    
    parser = TikTokParser()
    
    try:
        print("Testing TikTok parser...")
        result = await parser.parse_url(test_url)
        print("\nResults:")
        print(f"Title: {result['title']}")
        print(f"Views: {result['views']:,}")
        print(f"Likes: {result['likes']:,}")
        print(f"Comments: {result['comments']:,}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc() 