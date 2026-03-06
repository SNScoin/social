import requests

# Set your API base URL
BASE_URL = 'http://localhost:8000'

# Credentials (update if needed)
USERNAME = 'testuser'
PASSWORD = 'testpassword123'

# 1. Login to get access token
login_data = {
    'username': USERNAME,
    'password': PASSWORD
}

print('Logging in...')
resp = requests.post(f'{BASE_URL}/token', data=login_data)
if resp.status_code != 200:
    print('Login failed:', resp.text)
    exit(1)
token = resp.json().get('access_token')
if not token:
    print('No access token received!')
    exit(1)
print('Login successful. Token received.')

# 2. Fetch company stats
headers = {'Authorization': f'Bearer {token}'}
print('Fetching company stats...')
stats_resp = requests.get(f'{BASE_URL}/api/companies/2/stats', headers=headers)
print('Status code:', stats_resp.status_code)
print('Response:')
print(stats_resp.json()) 