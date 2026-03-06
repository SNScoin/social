import requests
import json

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "testuser"
PASSWORD = "testpassword123"
MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQyMjg4MTgzMCwiYWFpIjoxMSwidWlkIjo2NjUzMDM2NCwiaWFkIjoiMjAyNC0xMC0xM1QxMzo0ODozNS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjQwMzI2OTksInJnbiI6ImV1YzEifQ.Tw9iIQDXl0cppWYb0R4fyr_ndhTC8U2w_hwiEkU-r6U"


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


def get_companies(token):
    url = f"{BASE_URL}/api/companies"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"Companies status: {resp.status_code}")
    if resp.status_code == 200:
        companies = resp.json()
        print(f"Companies: {json.dumps(companies, indent=2)}")
        return companies
    print("Failed to fetch companies:", resp.text)
    return []


def connect_monday(token, company_id):
    url = f"{BASE_URL}/api/monday/connect"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "api_token": MONDAY_API_TOKEN,
        "company_id": company_id
    }
    resp = requests.post(url, headers=headers, json=data)
    print(f"Monday connect status: {resp.status_code}")
    print("Response:", resp.text)
    return resp.status_code == 200


def get_workspaces(token, company_id):
    url = f"{BASE_URL}/api/monday/workspaces?company_id={company_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"Workspaces status: {resp.status_code}")
    print("Response:", resp.text)
    if resp.status_code == 200:
        return resp.json()
    return []


def get_boards(token, company_id, workspace_id):
    url = f"{BASE_URL}/api/monday/boards?workspace_id={workspace_id}&company_id={company_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"Boards status: {resp.status_code}")
    print("Response:", resp.text)
    if resp.status_code == 200:
        return resp.json()
    return []


def get_items(token, company_id, board_id):
    url = f"{BASE_URL}/api/monday/items?board_id={board_id}&company_id={company_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"Items status: {resp.status_code}")
    print("Response:", resp.text)
    if resp.status_code == 200:
        return resp.json()
    return []


def main():
    token = login()
    if not token:
        return
    companies = get_companies(token)
    if not companies:
        print("No companies found.")
        return
    company_id = companies[0]["id"]
    print(f"Using company_id: {company_id}")
    if not connect_monday(token, company_id):
        print("Failed to connect to Monday.com")
        return
    workspaces = get_workspaces(token, company_id)
    if not workspaces:
        print("No workspaces found.")
        return
    workspace_id = workspaces[0]["id"]
    print(f"Using workspace_id: {workspace_id}")
    boards = get_boards(token, company_id, workspace_id)
    if not boards:
        print("No boards found.")
        return
    board_id = boards[0]["id"]
    print(f"Using board_id: {board_id}")
    items = get_items(token, company_id, board_id)
    print(f"Items: {json.dumps(items, indent=2)}")


if __name__ == "__main__":
    main() 