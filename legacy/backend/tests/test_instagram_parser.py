import asyncio
from backend.app.parsers.instagram_parser import InstagramParser

async def test_parser():
<<<<<<< HEAD
    url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"  # Updated with the provided URL
=======
    url = "https://www.instagram.com/p/DI_ZJccIGrX"  # Replace with a real/working Instagram post if needed
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    parser = InstagramParser()
    try:
        stats = await parser.parse_url(url)
        print("Fetched stats:")
        for k, v in stats.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_parser()) 