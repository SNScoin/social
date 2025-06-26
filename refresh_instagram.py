import requests
import json

url = "http://localhost:8000/api/links/refresh"
headers = {
    "Content-Type": "application/json"
}
data = {
    "url": "https://www.instagram.com/p/C7YwXxrP3Yt/?utm_source=ig_web_copy_link"
}

response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print("Response:")
print(json.dumps(response.json(), indent=2)) 