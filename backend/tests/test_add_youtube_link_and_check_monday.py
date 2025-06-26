import requests
import json

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "testuser"
PASSWORD = "testpassword123"
COMPANY_ID = 3
YOUTUBE_LINK = "https://www.youtube.com/shorts/JhkrbFq7pwE"


def login():
    url = f"{BASE_URL}/token"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(url, data=data, headers=headers)
    print(f"Login status: {resp.status_code}")
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print("Login failed:", resp.text)
    return None


def add_link(token):
    url = f"{BASE_URL}/api/links/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "url": YOUTUBE_LINK,
        "company_id": COMPANY_ID
    }
    resp = requests.post(url, headers=headers, json=data)
    print(f"Add link status: {resp.status_code}")
    print("Response:", resp.text)
    if resp.status_code == 200:
        return resp.json()
    return None


def main():
    token = login()
    if not token:
        return
    result = add_link(token)
    if result:
        print("Link added successfully!")
        print(json.dumps(result, indent=2))
        if "monday_item_id" in result:
            print(f"Monday.com sync item ID: {result['monday_item_id']}")
        else:
            print("No Monday.com sync info in response.")
    else:
        print("Failed to add link or sync with Monday.com.")


if __name__ == "__main__":
    main() 