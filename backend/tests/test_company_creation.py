import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_company_creation():
    # First, get the token
    login_url = "http://localhost:8000/token"
    login_data = {
        "username": "ROOT",
        "password": "admin123"
    }
    
    try:
        # Login to get token
        logger.info("Attempting to login...")
        login_response = requests.post(login_url, data=login_data)
        logger.debug(f"Login response status: {login_response.status_code}")
        logger.debug(f"Login response: {login_response.text}")
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        logger.info("Got token successfully")
        
        # Create company with unique name
        company_url = "http://localhost:8000/api/companies/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Use timestamp to ensure unique name
        unique_name = f"Test Company {datetime.now().strftime('%Y%m%d%H%M%S')}"
        company_data = {
            "name": unique_name
        }
        
        logger.info(f"\nAttempting to create company with name: {unique_name}")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request data: {company_data}")
        
        response = requests.post(company_url, headers=headers, json=company_data)
        logger.debug(f"Company creation response status: {response.status_code}")
        logger.debug(f"Company creation response: {response.text}")
        
        if response.status_code == 500:
            logger.error("Server error occurred. Check server logs for details.")
            logger.error(f"Response text: {response.text}")
            return
        
        response.raise_for_status()
        logger.info("Company created successfully")
        logger.debug(f"Response data: {response.json()}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"\nError: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            logger.error(f"Response headers: {e.response.headers}")
        raise

if __name__ == "__main__":
    test_company_creation() 