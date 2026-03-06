import re
import json

def extract_instagram_metrics_from_html():
    """Extract Instagram metrics from the saved HTML response"""
    
    try:
        # Read the saved HTML file
        with open('instagram_response.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔍 Extracting Instagram metrics from HTML...")
        
        # Extract metrics from meta description
        description_pattern = r'content="([^"]*likes[^"]*comments[^"]*)"'
        description_matches = re.findall(description_pattern, html_content)
        
        if description_matches:
            description = description_matches[0]
            print(f"✅ Found description: {description}")
            
            # Extract likes and comments
            likes_pattern = r'(\d+(?:,\d+)*)\s*likes'
            comments_pattern = r'(\d+(?:,\d+)*)\s*comments'
            
            likes_match = re.search(likes_pattern, description)
            comments_match = re.search(comments_pattern, description)
            
            likes = likes_match.group(1) if likes_match else "0"
            comments = comments_match.group(1) if comments_match else "0"
            
            # Extract username from description
            username_pattern = r'-\s*([^:]+):'
            username_match = re.search(username_pattern, description)
            username = username_match.group(1).strip() if username_match else "Unknown"
            
            # Extract caption text
            caption_pattern = r':\s*"([^"]+)"'
            caption_match = re.search(caption_pattern, description)
            caption = caption_match.group(1) if caption_match else ""
            
            # Extract date
            date_pattern = r'on\s+([^:]+):'
            date_match = re.search(date_pattern, description)
            date = date_match.group(1) if date_match else ""
            
            # Convert comma-separated numbers to integers
            likes_num = int(likes.replace(',', ''))
            comments_num = int(comments.replace(',', ''))
            
            metrics = {
                'username': username,
                'likes': likes_num,
                'comments': comments_num,
                'caption': caption,
                'date': date,
                'post_id': 'DLZEet2I6No',
                'platform': 'instagram',
                'url': 'https://www.instagram.com/reel/DLZEet2I6No/?utm_source=ig_web_copy_link'
            }
            
            print("\n📊 Extracted Instagram Metrics:")
            print("=" * 50)
            print(f"Username: {metrics['username']}")
            print(f"Likes: {metrics['likes']:,}")
            print(f"Comments: {metrics['comments']:,}")
            print(f"Caption: {metrics['caption']}")
            print(f"Date: {metrics['date']}")
            print(f"Post ID: {metrics['post_id']}")
            print(f"Platform: {metrics['platform']}")
            
            return metrics
            
        else:
            print("❌ No description found in HTML")
            return None
            
    except Exception as e:
        print(f"❌ Error extracting metrics: {str(e)}")
        return None

def test_instagram_parser_integration():
    """Test how this data would integrate with the existing parser"""
    
    print("\n🔧 Testing Integration with Existing Parser...")
    
    # Simulate what the parser should return
    extracted_data = extract_instagram_metrics_from_html()
    
    if extracted_data:
        # Format data to match parser output
        parser_output = {
            'title': extracted_data['caption'],
            'views': None,  # Instagram doesn't show views for reels in meta
            'likes': extracted_data['likes'],
            'comments': extracted_data['comments'],
            'owner': extracted_data['username'],
            'created_time': extracted_data['date'],
            'hashtags': re.findall(r'#(\w+)', extracted_data['caption']),
            'platform': 'instagram'
        }
        
        print("\n📋 Parser-Compatible Output:")
        print("=" * 50)
        print(json.dumps(parser_output, indent=2))
        
        print(f"\n✅ Success! Extracted {parser_output['likes']:,} likes and {parser_output['comments']:,} comments")
        print(f"✅ Username: {parser_output['owner']}")
        print(f"✅ Caption: {parser_output['title'][:100]}...")
        
        return parser_output
    else:
        print("❌ Failed to extract data")
        return None

if __name__ == "__main__":
    test_instagram_parser_integration() 