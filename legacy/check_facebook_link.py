import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/token"
ADD_LINK_URL = f"{API_URL}/api/links/"

# Step 1: Login to get JWT token
USERNAME = "testuser"  # Change if needed
PASSWORD = "testpassword123"  # Change if needed
COMPANY_ID = 8  # Change if needed
FACEBOOK_REEL_URL = "https://www.facebook.com/reel/1016000563989440"

login_data = {
    "username": USERNAME,
    "password": PASSWORD
}

logging.info("Logging in...")
logging.info(f"POST {LOGIN_URL} | data={login_data}")
login_response = requests.post(LOGIN_URL, data=login_data)
logging.info(f"Login status code: {login_response.status_code}")
try:
    login_json = login_response.json()
    logging.info(f"Login response: {login_json}")
    jwt_token = login_json.get("access_token")
except Exception:
    logging.error(f"Login response (non-JSON): {login_response.text}")
    jwt_token = None

if not jwt_token:
    logging.error("Failed to get JWT token. Exiting.")
    exit(1)

# Step 2: Add Facebook Reel link to company 8
payload = {
    "url": FACEBOOK_REEL_URL,
    "company_id": COMPANY_ID
}

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

logging.info(f"\nAdding Facebook Reel link to company {COMPANY_ID}...")
logging.info(f"POST {ADD_LINK_URL} | json={payload} | headers={{'Authorization': 'Bearer ...'}}")
response = requests.post(ADD_LINK_URL, json=payload, headers=headers)
logging.info(f"Add link status code: {response.status_code}")
try:
    logging.info(f"Add link response: {response.json()}")
except Exception:
    logging.error(f"Add link response (non-JSON): {response.text}") 