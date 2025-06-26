import requests
import json
import time

LOGIN_URL = "http://localhost:8000/token"
ADD_LINK_URL = "http://localhost:8000/api/links/"

USERNAME = "testuser"
PASSWORD = "testpassword123"
COMPANY_ID = 2
INSTAGRAM_URL = "https://www.instagram.com/p/DI_ZJccIGrX"

def get_auth_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(LOGIN_URL, data=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"Login failed: {response.text}")
    return None

def add_instagram_link(token):
    headers = {"Authorization": f"Bearer {token}"}
    add_data = {
        "url": INSTAGRAM_URL,
        "company_id": COMPANY_ID
    }
    response = requests.post(ADD_LINK_URL, json=add_data, headers=headers)
    print(f"Add link response: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)

if __name__ == "__main__":
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        exit(1)
    add_instagram_link(token) 