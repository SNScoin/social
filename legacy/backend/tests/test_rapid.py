import requests
import json

def test_rapid_api():
    url = "https://scrapeninja.p.rapidapi.com/scrape"
    
    querystring = {"url": "https://www.instagram.com/reels/DIEj1QZN22_/"}
    
    headers = {
        "x-rapidapi-host": "scrapeninja.p.rapidapi.com",
        "x-rapidapi-key": "686292c58amshc864cb048af6661c8f45jsna2dbcc01f184"
    }
    
    print("Making request to RapidAPI...")
    response = requests.get(url, headers=headers, params=querystring)
    print(f"Status Code: {response.status_code}")
    print("\nResponse Headers:")
    print(json.dumps(dict(response.headers), indent=2))
    print("\nResponse Body:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_rapid_api() 