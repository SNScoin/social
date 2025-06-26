import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
import json
import traceback
from backend.tests.test_credentials import USERNAME, EMAIL, PASSWORD

def test_companies_api():
    try:
        base_url = "http://127.0.0.1:8000"
        
        # First register a test user
        print("\nRegistering test user...")
        register_data = {
            "email": EMAIL,
            "password": PASSWORD,
            "full_name": "Test User"
        }
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=register_data
        )
        print(f"Register response status: {register_response.status_code}")
        print(f"Register response: {register_response.text}")
        
        # Test with authentication
        print("\nTesting with authentication...")
        login_data = {
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        print("Attempting to get token...")
        token_response = requests.post(
            f"{base_url}/token",
            data=login_data
        )
        print(f"Token response status: {token_response.status_code}")
        print(f"Token response: {token_response.text}")
        
        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create a test company
            print("\nCreating test company...")
            company_data = {
                "name": "Te Company"
            }
            create_response = requests.post(
                f"{base_url}/api/companies/",
                headers=headers,
                json=company_data
            )
            print(f"Create company status: {create_response.status_code}")
            print(f"Create company response: {create_response.text}")
            
            # Now try to get companies
            print("\nGetting companies...")
            response = requests.get(
                f"{base_url}/api/companies/",
                headers=headers
            )
            print(f"Get companies status: {response.status_code}")
            try:
                companies = response.json()
                print("Companies list:")
                print(json.dumps(companies, indent=2))
            except:
                print(f"Response: {response.text}")
        else:
            print("Failed to get token")
            print(f"Status code: {token_response.status_code}")
            print(f"Response: {token_response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

def test_company_stats():
    try:
        base_url = "http://127.0.0.1:8000"
        login_data = {
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        token_response = requests.post(f"{base_url}/token", data=login_data)
        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            stats_response = requests.get(f"{base_url}/api/companies/2/stats", headers=headers)
            print(f"Stats response status: {stats_response.status_code}")
            print(f"Stats response: {stats_response.text}")
        else:
            print("Failed to get token for stats test")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

def test_links_api():
    try:
        base_url = "http://127.0.0.1:8000"
        login_data = {
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        token_response = requests.post(f"{base_url}/token", data=login_data)
        if token_response.status_code == 200:
            token = token_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            # Fetch companies
            companies_response = requests.get(f"{base_url}/api/companies/", headers=headers)
            companies = companies_response.json()
            if not companies:
                print("No companies found for user.")
                return
            company_id = companies[0]["id"]
            print(f"Using company_id: {company_id}")
            # Fetch links for the company
            response = requests.get(f"{base_url}/api/links/?company_id={company_id}", headers=headers)
            print(f"Links API status: {response.status_code}")
            try:
                links = response.json()
                print("Links API response:")
                print(json.dumps(links, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"Error parsing response: {str(e)}")
                print(f"Raw response: {response.text}")
        else:
            print("Failed to get token for links API test")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    # test_companies_api()
    # test_company_stats()
    test_links_api() 