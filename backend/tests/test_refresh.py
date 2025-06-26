import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test URLs for each platform - using real, working links
TEST_LINKS = {
    'youtube': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
    'tiktok': 'https://www.tiktok.com/@tiktok/video/7316780105202765102',  # Official TikTok account
    'instagram': 'https://www.instagram.com/reel/C4Yz123ABC/',  # Example Instagram reel
    'facebook': 'https://www.facebook.com/reel/3139447296208152'  # Your Facebook reel
}

def get_auth_token():
    # Login to get token
    login_url = "http://localhost:8000/token"
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    try:
        response = requests.post(login_url, data=login_data)  # Note: using data instead of json
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            return response.json().get("access_token")
        print(f"Login failed: {response.text}")
    except Exception as e:
        print(f"Login error: {e}")
    return None

def test_add_and_refresh():
    # First login to get token
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post('http://localhost:8000/token', data=login_data)
    if response.status_code != 200:
        print("Login failed:", response.text)
        return
        
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Add test links
    for platform, url in TEST_LINKS.items():
        print(f"\nTesting {platform.upper()} link:")
        print(f"Adding link: {url}")
        
        # Add link
        add_data = {
            "url": url,
            "company_id": 1  # Assuming company ID 1 exists
        }
        
        response = requests.post(
            'http://localhost:8000/api/links/',
            json=add_data,
            headers=headers
        )
        
        if response.status_code == 200:
            link_id = response.json()['id']
            print(f"Link added successfully. ID: {link_id}")
            
            # Wait a bit before refreshing
            time.sleep(2)
            
            # Test refresh
            print(f"Refreshing link ID: {link_id}")
            refresh_response = requests.post(
                f'http://localhost:8000/api/links/{link_id}/refresh',
                headers=headers
            )
            
            if refresh_response.status_code == 200:
                print("Refresh successful!")
                print("Response:", refresh_response.json())
            else:
                print("Refresh failed:", refresh_response.text)
        else:
            print("Failed to add link:", response.text)

def test_refresh_link(link_id, token):
    url = f"http://localhost:8000/api/links/{link_id}/refresh"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, headers=headers)
        print(f"\nTesting refresh for link ID: {link_id}")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        exit(1)
    
    # Test Instagram link (ID: 17)
    test_refresh_link(17, token) 