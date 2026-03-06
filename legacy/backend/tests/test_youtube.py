import asyncio
import traceback
from parsers.youtube_parser import YouTubeParser

async def main():
    # Test URL - a popular YouTube video
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        parser = YouTubeParser()
        result = await parser.parse_url(url)
        
        if result:
            print("\nYouTube Video Data:")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Views: {result.get('views', 'N/A')}")
            print(f"Likes: {result.get('likes', 'N/A')}")
            print(f"Comments: {result.get('comments', 'N/A')}")
        else:
            print("Failed to parse YouTube video data")
            
    except Exception as e:
        print(f"Error while parsing YouTube URL: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc() 