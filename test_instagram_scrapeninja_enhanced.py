import requests
import json
from bs4 import BeautifulSoup
import re

def extract_detailed_metadata_from_html(html_content):
    """Enhanced metadata extraction from Instagram HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {}
    
    try:
        print("🔍 Analyzing HTML content...")
        
        # Extract username from various possible locations
        username_selectors = [
            'a[href*="/"] span',  # Username in links
            'div[class*="username"]',  # Username divs
            'span[class*="username"]',  # Username spans
            'a[class*="username"]'  # Username links
        ]
        
        for selector in username_selectors:
            username_elem = soup.select_one(selector)
            if username_elem and username_elem.get_text().strip():
                metadata['username'] = username_elem.get_text().strip()
                print(f"✅ Found username: {metadata['username']}")
                break
        
        # Extract caption/text content
        caption_selectors = [
            'div[class*="caption"]',
            'div[class*="text"]',
            'span[class*="caption"]',
            'div[data-testid*="caption"]'
        ]
        
        for selector in caption_selectors:
            caption_elem = soup.select_one(selector)
            if caption_elem and caption_elem.get_text().strip():
                caption_text = caption_elem.get_text().strip()
                if len(caption_text) > 10:  # Only if it's substantial
                    metadata['caption'] = caption_text[:200] + "..." if len(caption_text) > 200 else caption_text
                    print(f"✅ Found caption: {metadata['caption'][:50]}...")
                    break
        
        # Extract engagement metrics
        engagement_patterns = [
            r'(\d+(?:\.\d+)?[KMB]?)\s*(likes?|views?|comments?)',
            r'(\d+(?:,\d+)*)\s*(likes?|views?|comments?)'
        ]
        
        page_text = soup.get_text()
        for pattern in engagement_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                value, metric_type = match
                metric_type = metric_type.lower().rstrip('s')
                if metric_type in ['like', 'view', 'comment']:
                    metadata[f'{metric_type}s'] = value
                    print(f"✅ Found {metric_type}s: {value}")
        
        # Extract video/image URLs
        media_elements = soup.find_all(['video', 'img'])
        media_urls = []
        for elem in media_elements:
            src = elem.get('src') or elem.get('data-src')
            if src and 'instagram' in src:
                media_urls.append(src)
        
        if media_urls:
            metadata['media_urls'] = media_urls[:3]  # Limit to first 3
            print(f"✅ Found {len(media_urls)} media URLs")
        
        # Look for JSON data in script tags
        script_tags = soup.find_all('script', {'type': 'application/json'})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Look for Instagram-specific data structures
                    if 'require' in data or 'instagr' in str(data).lower():
                        metadata['json_data_found'] = True
                        print("✅ Found JSON data in script tags")
                        break
            except:
                continue
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', page_text)
        if hashtags:
            metadata['hashtags'] = hashtags[:10]  # Limit to first 10
            print(f"✅ Found {len(hashtags)} hashtags")
        
        # Extract post ID from URL patterns in the HTML
        post_id_patterns = [
            r'instagram\.com/(?:p|reel)/([^/]+)',
            r'media_id["\']:\s*["\']([^"\']+)["\']',
            r'post_id["\']:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in post_id_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                metadata['post_id'] = matches[0]
                print(f"✅ Found post ID: {metadata['post_id']}")
                break
        
    except Exception as e:
        metadata['error'] = str(e)
        print(f"❌ Error during extraction: {str(e)}")
    
    return metadata

def test_instagram_scrapeninja_enhanced():
    """Enhanced Instagram scraping test using ScrapeNinja"""
    url = "https://scrapeninja.p.rapidapi.com/scrape"
    
    target_url = "https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link"
    
    headers = {
        "x-rapidapi-key": "686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184",
        "x-rapidapi-host": "scrapeninja.p.rapidapi.com"
    }
    
    params = {
        "url": target_url,
        "render": "true",  # Enable JavaScript rendering
        "wait": "2000"     # Wait 2 seconds for content to load
    }
    
    try:
        print("🚀 Starting enhanced Instagram scraping test...")
        print(f"📱 Target URL: {target_url}")
        print("⏳ Making request to ScrapeNinja API...")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"\n📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Extract HTML content from the response body
                if 'body' in data:
                    html_content = data['body']
                    print(f"\n📄 HTML Content Length: {len(html_content)} characters")
                    
                    # Save HTML for debugging
                    with open('instagram_response.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("💾 Saved HTML response to 'instagram_response.html'")
                    
                    print("\n🔍 Parsing HTML content...")
                    metadata = extract_detailed_metadata_from_html(html_content)
                    
                    print("\n📋 Extracted Metadata:")
                    print("=" * 50)
                    print(json.dumps(metadata, indent=2, ensure_ascii=False))
                    
                    # Summary
                    print("\n📈 Summary:")
                    print(f"✅ Username: {metadata.get('username', 'Not found')}")
                    print(f"✅ Caption: {metadata.get('caption', 'Not found')[:50]}...")
                    print(f"✅ Likes: {metadata.get('likes', 'Not found')}")
                    print(f"✅ Views: {metadata.get('views', 'Not found')}")
                    print(f"✅ Comments: {metadata.get('comments', 'Not found')}")
                    print(f"✅ Post ID: {metadata.get('post_id', 'Not found')}")
                    print(f"✅ Hashtags: {len(metadata.get('hashtags', []))} found")
                    
                else:
                    print("\n❌ No HTML content found in response body")
                    print("Response structure:", json.dumps(list(data.keys()), indent=2))
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse JSON response: {str(e)}")
                print("Raw response:", response.text[:500])
        else:
            print(f"\n❌ Error Response Content:")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instagram_scrapeninja_enhanced() 