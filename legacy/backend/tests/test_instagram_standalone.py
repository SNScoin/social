import asyncio
from backend.app.parsers.instagram_parser import InstagramParser

async def test_instagram_parser():
    print("Testing Instagram parser...")
    try:
        parser = InstagramParser()
<<<<<<< HEAD
        # Test with the provided Reel URL
        url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
=======
        # Test with a public Reels URL
        url = "https://www.instagram.com/reels/DIEj1QZN22_/"
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        print(f"\nTesting URL: {url}")
        data = await parser.parse_url(url)
        print("\nParsed data:")
        print(f"Title: {data['title']}")
        print(f"Views: {data['views']}")
        print(f"Likes: {data['likes']}")
        print(f"Comments: {data['comments']}")
<<<<<<< HEAD
        if 'error' in data:
            print(f"Error: {data['error']}")
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_instagram_parser()) 