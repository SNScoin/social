import asyncio
from backend.app.parsers.instagram_parser import InstagramParser

async def test_instagram_parser():
    print("Testing Instagram parser...")
    try:
        parser = InstagramParser()
        # Test with a public Reels URL
        url = "https://www.instagram.com/reels/DIEj1QZN22_/"
        print(f"\nTesting URL: {url}")
        data = await parser.parse_url(url)
        print("\nParsed data:")
        print(f"Title: {data['title']}")
        print(f"Views: {data['views']}")
        print(f"Likes: {data['likes']}")
        print(f"Comments: {data['comments']}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 