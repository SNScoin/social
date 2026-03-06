import re

def validate_social_url(url: str) -> tuple[str, str]:
    """
    Validate and normalize social media URLs.
    Returns a tuple of (normalized_url, platform)
    """
    url = url.strip()
    
    # Instagram validation
    instagram_pattern = r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:p|reel)\/([a-zA-Z0-9_-]+)'
    instagram_match = re.match(instagram_pattern, url)
    if instagram_match:
        normalized_url = f'https://www.instagram.com/p/{instagram_match.group(1)}'
        return normalized_url, 'instagram'
    
    # TikTok validation
    tiktok_pattern = r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([^\/]+)\/video\/(\d+)'
    tiktok_match = re.match(tiktok_pattern, url)
    if tiktok_match:
        username, video_id = tiktok_match.group(1), tiktok_match.group(2)
        normalized_url = f'https://www.tiktok.com/@{username}/video/{video_id}'
        return normalized_url, 'tiktok'
    
    # Short TikTok URL validation
    short_tiktok_pattern = r'(?:https?:\/\/)?(?:www\.)?vm\.tiktok\.com\/([a-zA-Z0-9]+)'
    short_tiktok_match = re.match(short_tiktok_pattern, url)
    if short_tiktok_match:
        # For short URLs, we'll keep them as is since we can't extract username
        normalized_url = f'https://vm.tiktok.com/{short_tiktok_match.group(1)}'
        return normalized_url, 'tiktok'
    
    # YouTube validation
    youtube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in youtube_patterns:
        youtube_match = re.match(pattern, url)
        if youtube_match:
            video_id = youtube_match.group(1)
            normalized_url = f'https://www.youtube.com/watch?v={video_id}'
            return normalized_url, 'youtube'
    
    # Facebook validation
    facebook_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/reel\/(\d+)',
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/.*\/videos\/(\d+)',
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/watch\/\?v=(\d+)'
    ]
    
    for pattern in facebook_patterns:
        facebook_match = re.match(pattern, url)
        if facebook_match:
            video_id = facebook_match.group(1)
            normalized_url = f'https://www.facebook.com/reel/{video_id}'
            return normalized_url, 'facebook'
    
    raise ValueError("Invalid social media URL. Supported platforms: Instagram, TikTok, YouTube, Facebook") 