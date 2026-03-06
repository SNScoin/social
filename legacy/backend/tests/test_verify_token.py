import requests

def login():
    url = "http://127.0.0.1:8000/token"
    data = {
        "username": "testuser",
        "password": "test123"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers)
        print(f"Login Status Code: {response.status_code}")
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login Response: {response.json()}")
            return None
    except Exception as e:
        print(f"Login Error: {str(e)}")
        return None

def connect_monday(access_token):
    url = "http://127.0.0.1:8000/api/monday/connect"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "api_token": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQyMjg4MTgzMCwiYWFpIjoxMSwidWlkIjo2NjUzMDM2NCwiaWFkIjoiMjAyNC0xMC0xM1QxMzo0ODozNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjQwMzI2OTksInJnbiI6ImV1YzEifQ.Tw9iIQDXl0cppWYb0R4fyr_ndhTC8U2w_hwiEkU-r6U"  # Replace with your actual Monday.com API token
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Connect Status Code: {response.status_code}")
        print(f"Connect Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Connect Error: {str(e)}")
        return False

def test_verify_token():
    # First login to get access token
    access_token = login()
    if not access_token:
        print("Failed to get access token")
        return
        
    # Connect to Monday.com
    if not connect_monday(access_token):
        print("Failed to connect to Monday.com")
        return
        
    # Now verify the token
    url = "http://127.0.0.1:8000/api/monday/verify_token"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Verify Token Status Code: {response.status_code}")
        print(f"Verify Token Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_verify_token() 