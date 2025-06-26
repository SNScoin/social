import requests
import json

def test_add_facebook_link():
    url = "http://localhost:8000/api/links/"
    data = {
        "url": "https://www.facebook.com/reel/123456789"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_add_facebook_link() 