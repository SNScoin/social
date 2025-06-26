import asyncio
import json
from backend.app.parsers.instagram_parser import InstagramParser

async def test_instagram_parser():
    print("Starting Instagram parser test...")
    
    try:
        # Initialize parser
        parser = InstagramParser()
        print("Parser initialized successfully")
        
        # Test URLs - let's try both a reel and a post
        test_urls = [
            "https://www.instagram.com/reels/DIEj1QZN22_/",
            "https://www.instagram.com/reel/DHVPQMjSD08/"
        ]
        
        for url in test_urls:
            print(f"\n{'='*50}")
            print(f"Testing URL: {url}")
            
            # Test URL validation
            print("\nValidating URL...")
            is_valid = parser.validate_url(url)
            print(f"URL validation result: {is_valid}")
            
            if not is_valid:
                print("URL validation failed, skipping...")
                continue
            
            # Parse URL
            print("\nParsing URL...")
            try:
                data = await parser._get_instagram_data(url)
                print("\nRaw API Response:")
                print(json.dumps(data, indent=2))
                
                print("\nParsed Data:")
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Views: {data.get('views', 0)}")
                print(f"Likes: {data.get('likes', 0)}")
                print(f"Comments: {data.get('comments', 0)}")
                
            except Exception as e:
                print(f"\nError during parsing: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                raise
                
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 