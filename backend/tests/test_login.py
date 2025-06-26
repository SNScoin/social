import requests
import json

def test_login(username, password):
    url = "http://localhost:8000/token"
    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    
    try:
        response = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("Login successful!")
            print("Access token received")
            return True
        else:
            print(f"Login failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing login with testuser...")
    test_login("testuser", "test123") 