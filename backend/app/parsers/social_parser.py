import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
import json
from backend.app.models.models import Platform

class SocialMediaParser:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def parse_youtube(self, url: str) -> Optional[Dict]:
        try:
            # Extract video ID from URL
            video_id = None
            if 'youtube.com/watch?v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]

            if not video_id:
                return None

            # Make request to YouTube
            response = requests.get(f'https://www.youtube.com/watch?v={video_id}', headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.find('title').text.replace(' - YouTube', '')

            # Extract statistics from the page
            stats = {}
            for script in soup.find_all('script'):
                if 'var ytInitialData' in script.text:
                    data = json.loads(script.text.split('var ytInitialData = ')[1].split(';')[0])
                    
                    # Get video stats
                    video_renderer = None
                    for item in data['contents']['twoColumnWatchNextResults']['results']['results']['contents']:
                        if 'videoPrimaryInfoRenderer' in item:
                            video_renderer = item['videoPrimaryInfoRenderer']
                            break

                    if video_renderer:
                        # Get views
                        views_text = video_renderer['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
                        views = int(re.sub(r'[^\d]', '', views_text))

                        # Get likes
                        likes_text = video_renderer['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label']
                        likes = int(re.sub(r'[^\d]', '', likes_text))

                        stats = {
                            'title': title,
                            'views': views,
                            'likes': likes,
                            'comments': 0  # Comments require additional API calls
                        }
                        return stats

        except Exception as e:
            print(f"Error parsing YouTube video: {str(e)}")
        return None

    def parse_tiktok(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title from meta tags
            title = soup.find('meta', property='og:title')['content']

            # Extract statistics
            stats = {
                'title': title,
                'views': 0,
                'likes': 0,
                'comments': 0
            }

            # Note: TikTok requires their API for accurate stats
            # This is a basic implementation that might not work due to TikTok's anti-scraping measures
            return stats

        except Exception as e:
            print(f"Error parsing TikTok video: {str(e)}")
        return None

    def parse_instagram(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title from meta tags
            title = soup.find('meta', property='og:title')['content']

            # Extract statistics
            stats = {
                'title': title,
                'views': 0,
                'likes': 0,
                'comments': 0
            }

            # Note: Instagram requires their API for accurate stats
            # This is a basic implementation that might not work due to Instagram's anti-scraping measures
            return stats

        except Exception as e:
            print(f"Error parsing Instagram post: {str(e)}")
        return None

    def parse_link(self, url: str) -> Optional[Dict]:
        if 'youtube.com' in url or 'youtu.be' in url:
            return self.parse_youtube(url)
        elif 'tiktok.com' in url:
            return self.parse_tiktok(url)
        elif 'instagram.com' in url:
            return self.parse_instagram(url)
        else:
            print("Unsupported platform")
            return None

def main():
    parser = SocialMediaParser()
    
    while True:
        url = input("Enter social media link (or 'quit' to exit): ")
        if url.lower() == 'quit':
            break

        stats = parser.parse_link(url)
        if stats:
            print("\nParsed Statistics:")
            print(f"Title: {stats['title']}")
            print(f"Views: {stats['views']}")
            print(f"Likes: {stats['likes']}")
            print(f"Comments: {stats['comments']}")
        else:
            print("Could not parse the link. Please make sure it's a valid YouTube, TikTok, or Instagram link.")

if __name__ == "__main__":
    main() 