import json
import re

def extract_instagram_view_count():
    """Extract Instagram view count from the saved HTML response"""
    
    try:
        # Read the saved HTML file
        with open('instagram_response.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print("🔍 Extracting Instagram view count from HTML...")
        
        # Look for the specific JSON data containing view_count
        # The pattern shows: "view_count":null or "view_count":number
        view_count_pattern = r'"view_count":(\d+|null)'
        view_count_matches = re.findall(view_count_pattern, html_content)
        
        print(f"✅ Found {len(view_count_matches)} view_count entries")
        
        # Look for the main post data (the first occurrence is usually the main post)
        main_post_pattern = r'"shortcode":"DLZEet2I6No".*?"view_count":(\d+|null)'
        main_post_match = re.search(main_post_pattern, html_content, re.DOTALL)
        
        if main_post_match:
            view_count = main_post_match.group(1)
            print(f"✅ Main post view count: {view_count}")
            
            if view_count == 'null':
                print("⚠️  View count is null - Instagram may not display view counts for this reel")
            else:
                print(f"🎉 Successfully extracted view count: {view_count}")
        else:
            print("❌ Could not find main post view count")
        
        # Also look for like_and_view_counts_disabled field
        disabled_pattern = r'"like_and_view_counts_disabled":(true|false)'
        disabled_matches = re.findall(disabled_pattern, html_content)
        
        if disabled_matches:
            print(f"✅ Like and view counts disabled: {disabled_matches[0]}")
        
        # Extract other metrics for comparison
        like_count_pattern = r'"like_count":(\d+)'
        like_count_matches = re.findall(like_count_pattern, html_content)
        
        comment_count_pattern = r'"comment_count":(\d+)'
        comment_count_matches = re.findall(comment_count_pattern, html_content)
        
        print(f"\n📊 Summary of found metrics:")
        print(f"   View counts found: {len(view_count_matches)}")
        print(f"   Like counts found: {len(like_count_matches)}")
        print(f"   Comment counts found: {len(comment_count_matches)}")
        
        # Show first few values for each metric
        if view_count_matches:
            print(f"   Sample view counts: {view_count_matches[:5]}")
        if like_count_matches:
            print(f"   Sample like counts: {like_count_matches[:5]}")
        if comment_count_matches:
            print(f"   Sample comment counts: {comment_count_matches[:5]}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    extract_instagram_view_count() 