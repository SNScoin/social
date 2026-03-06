import requests
import json
from bs4 import BeautifulSoup
import re

def extract_metadata_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {}
    
    try:
        # Extract username
        username_div = soup.find('div', string=lambda text: text and '@' not in text and text.strip() and not text.startswith('•'))
        if username_div:
            metadata['username'] = username_div.get_text().strip()
        
        # Extract caption
        caption_div = soup.find('div', {'class': re.compile(r'x1g9anri.*x78zum5.*xvs91rp.*xmix8c7')})
        if caption_div:
            metadata['caption'] = caption_div.get_text().strip()
        
        # Extract engagement metrics (likes, comments)
        engagement_spans = soup.find_all('span', {'class': re.compile(r'xdj266r.*x11i5rnm.*xat24cr')})
        for span in engagement_spans:
            text = span.get_text().strip()
            if 'K' in text:
                if 'likes' not in metadata:
                    metadata['likes'] = text
                else:
                    metadata['comments'] = text
        
        # Extract video URL if available
        video_element = soup.find('video')
        if video_element:
            metadata['video_url'] = video_element.get('src', '')
        
        # Look for any script tags containing video data
        script_tags = soup.find_all('script', {'type': 'application/json'})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'require' in data:
                    metadata['video_data_found'] = True
                    break
            except:
                continue
        
    except Exception as e:
        metadata['error'] = str(e)
    
    return metadata

def test_instagram_scraping():
    url = "https://scrapeninja.p.rapidapi.com/scrape"
    
<<<<<<< HEAD
    querystring = {"url": "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"}
=======
    querystring = {"url": "https://www.instagram.com/reels/DIEj1QZN22_/"}
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    
    headers = {
        "x-rapidapi-key": "686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184",
        "x-rapidapi-host": "scrapeninja.p.rapidapi.com"
    }
    
    try:
        print("Making request to ScrapeNinja API...")
<<<<<<< HEAD
        print(f"Target URL: {querystring['url']}")
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        response = requests.get(url, headers=headers, params=querystring)
        
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Extract HTML content from the response body
                if 'body' in data:
                    html_content = data['body']
                    print("\nParsing HTML content...")
                    metadata = extract_metadata_from_html(html_content)
                    
                    print("\nExtracted Metadata:")
                    print(json.dumps(metadata, indent=2))
                else:
                    print("\nNo HTML content found in response body")
                    print("Response structure:", json.dumps(data.keys(), indent=2))
            except json.JSONDecodeError as e:
                print("\nFailed to parse JSON response:", str(e))
                print("Raw response:", response.text[:500])
        else:
            print(f"\nError Response Content:")
            print(response.text)
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    test_instagram_scraping() 