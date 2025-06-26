import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_links_api():
    # Login and get token
    login_data = {
        "username": "testuser",
        "password": "testpassword123"  # Make sure this matches your test user's password
    }
    
    try:
        logger.info("Attempting to login...")
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        logger.info(f"Login response status: {response.status_code}")
        logger.info(f"Login response: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Login failed with status {response.status_code}")
            return
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        logger.info("Login successful")
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return

    # Get companies
    try:
        response = requests.get(f"{BASE_URL}/api/companies/", headers=headers)
        response.raise_for_status()
        companies = response.json()
        if not companies:
            logger.error("No companies found")
            return
        company_id = companies[0]["id"]
        logger.info(f"Using company ID: {company_id}")
    except Exception as e:
        logger.error(f"Failed to get companies: {str(e)}")
        return

    # Add a test link
    logger.info("\nAdding a test link...")
    link_data = {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "company_id": company_id,
        "platform": "youtube"
    }
    logger.info(f"Link data: {json.dumps(link_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/links/", json=link_data, headers=headers)
        logger.info(f"Add link status: {response.status_code}")
        logger.info(f"Add link response: {response.text}")
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to add link: {str(e)}")

    # Get links
    logger.info("\nGetting links...")
    try:
        response = requests.get(f"{BASE_URL}/api/links/?company_id={company_id}", headers=headers)
        logger.info(f"Get links status: {response.status_code}")
        logger.info(f"Get links response: {response.text}")
        response.raise_for_status()
        links = response.json()
        logger.info("Links list:")
        logger.info(json.dumps(links, indent=2))
    except Exception as e:
        logger.error(f"Failed to get links: {str(e)}")

if __name__ == "__main__":
    test_links_api() 