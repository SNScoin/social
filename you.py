from googleapiclient.discovery import build

# Hardcoded API Key
API_KEY = "AIzaSyBJh8PvT1avBVd01qUIrONkL4mBFFJaW1o"

def get_youtube_video_data(video_id):
    # Initialize the YouTube API client with the hardcoded API key
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # Request video data from the YouTube Data API
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    # Extract data from the response
    if 'items' in response and len(response['items']) > 0:
        video_data = response['items'][0]
        title = video_data['snippet']['title']
        likes = video_data['statistics'].get('likeCount', 'Not available')
        views = video_data['statistics'].get('viewCount', 'Not available')
        comments = video_data['statistics'].get('commentCount', 'Not available')

        return {
            "title": title,
            "likes": likes,
            "views": views,
            "comments": comments
        }
    else:
        return "Video not found or data not accessible."

if __name__ == "__main__":
    video_url = input("Enter YouTube Shorts URL: ")

    # Extract the video ID from the YouTube URL
    video_id = video_url.split('/')[-1] if "shorts" in video_url else None

    if video_id:
        data = get_youtube_video_data(video_id)
        print(data)
    else:
        print("Invalid YouTube Shorts URL.")
