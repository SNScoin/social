import requests
import json

# Set your API base URL
BASE_URL = 'http://localhost:8000'

# Credentials
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

# 2. Add a new TikTok link
headers = {'Authorization': f'Bearer {token}'}

# Test TikTok link
tiktok_link_data = {
    'url': 'https://www.tiktok.com/@kabooke12/video/7457851293294447878',
    'company_id': 8  # Use company 8 as shown in the logs
}

print('Adding TikTok link...')
print(f'URL: {tiktok_link_data["url"]}')
print(f'Company ID: {tiktok_link_data["company_id"]}')

add_resp = requests.post(f'{BASE_URL}/api/links/', json=tiktok_link_data, headers=headers)
print('Status code:', add_resp.status_code)
print('Response:')
print(json.dumps(add_resp.json(), indent=2))

if add_resp.status_code == 200:
    link_data = add_resp.json()
    metrics = link_data.get('metrics', {})
    print(f'\n✓ Link added successfully!')
    print(f'Link ID: {link_data.get("id")}')
    print(f'Title: {link_data.get("title")}')
    print(f'Platform: {link_data.get("platform")}')
    print(f'Views: {metrics.get("views", 0)}')
    print(f'Likes: {metrics.get("likes", 0)}')
    print(f'Comments: {metrics.get("comments", 0)}')
    
    if metrics.get("views", 0) > 0:
        print('🎉 TikTok parser is working correctly!')
    else:
        print('❌ TikTok parser still returning zeros')
else:
    print('❌ Failed to add link') 