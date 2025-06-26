import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"  # Update this if your server runs on a different port
TEST_USER = {
    "email": "testuser",
    "password": "testpassword123"
}

def test_add_link_without_monday():
    """Test adding a link without Monday.com configuration"""
    try:
        # 1. Login to get auth token
        logger.info("Attempting to login...")
        try:
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=TEST_USER
            )
            login_response.raise_for_status()
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            logger.info("Successfully logged in")
        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return False
        
        # 2. Get user's companies
        logger.info("Fetching user's companies...")
        try:
            companies_response = requests.get(
                f"{BASE_URL}/api/companies",
                headers=headers
            )
            companies_response.raise_for_status()
            companies = companies_response.json()
            logger.info(f"Found {len(companies)} companies")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch companies: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return False
        
        if not companies:
            logger.error("No companies found for test user")
            return False
            
        company_id = companies[0]["id"]
        logger.info(f"Using company ID: {company_id}")
        
        # 3. Add a test link
        test_link = {
            "url": "https://www.instagram.com/reel/ABC123/",
            "company_id": company_id
        }
        
        logger.info("Attempting to add test link...")
        try:
            link_response = requests.post(
                f"{BASE_URL}/api/links/",
                json=test_link,
                headers=headers
            )
            
            if link_response.status_code == 200:
                logger.info("Successfully added link without Monday.com configuration")
                result = link_response.json()
                logger.info(f"Link added with ID: {result['id']}")
                logger.info(f"Platform: {result['platform']}")
                logger.info(f"Stats: {json.dumps(result['stats'], indent=2)}")
                return True
            else:
                logger.error(f"Failed to add link: {link_response.status_code}")
                logger.error(f"Response: {link_response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add link: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting test: Adding link without Monday.com configuration")
    success = test_add_link_without_monday()
    logger.info(f"Test {'passed' if success else 'failed'}") 