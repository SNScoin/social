import asyncio
from backend.app.parsers.instagram_parser import InstagramParser

async def test_instagram_parser():
    print("Testing Instagram parser...")
    try:
        parser = InstagramParser()
        # Test with the provided Reel URL
        url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
        print(f"\nTesting URL: {url}")
        data = await parser.parse_url(url)
        print("\nParsed data:")
        print(f"Title: {data['title']}")
        print(f"Views: {data['views']}")
        print(f"Likes: {data['likes']}")
        print(f"Comments: {data['comments']}")
        if 'error' in data:
            print(f"Error: {data['error']}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 