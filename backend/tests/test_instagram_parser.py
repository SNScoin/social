import asyncio
from backend.app.parsers.instagram_parser import InstagramParser

async def test_parser():
    url = "https://www.instagram.com/p/DI_ZJccIGrX"  # Replace with a real/working Instagram post if needed
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