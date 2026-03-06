import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
TEST_LINK = "https://www.youtube.com/shorts/lgVV2F7ciKE"  # New unique YouTube Shorts link
COMPANY_ID = 2  # Use company 2 for this test

def login():
    """Login and get access token"""
    print("\nLogging in...")
    data = {
        "username": "testuser",
        "password": "testpassword123",
        "grant_type": "password"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(f"{BASE_URL}/token", data=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def add_link(token, company_id):
    """Add a new link and verify Monday.com item ID in response"""
    print("\nAdding new link...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "url": TEST_LINK,
        "company_id": company_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/links/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("\nAdd Link Response:")
        print(json.dumps(result, indent=2))
        
        # Verify Monday.com item ID
        if result.get('monday_item_id'):
            print("\n✅ Monday.com item ID found in response!")
            print(f"Monday.com item ID: {result['monday_item_id']}")
        else:
            print("\n❌ Monday.com item ID missing from response!")
        
        return result
    else:
        print(f"Error: {response.text}")
        return None

def main():
    token = login()
    if not token:
        return
    result = add_link(token, COMPANY_ID)
    if result:
        print("\nTest completed!")
    else:
        print("\nTest failed!")

if __name__ == "__main__":
    main() 