import http.client
import json

def test_scrape_ninja():
    conn = http.client.HTTPSConnection("scrapeninja.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "686292c56amsh1c864cb048af666p1c8f45jsna2dbcc01f184",
        'x-rapidapi-host': "scrapeninja.p.rapidapi.com"
    }

    # First test with the sample URL
    test_url = "/scrape?url=https%3A%2F%2Fapiroad.net%2Fajax-test.html"
    print(f"\nTesting with sample URL: {test_url}")
    conn.request("GET", test_url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print("\nResponse Status:", res.status)
    print("\nResponse Headers:")
    print(json.dumps(dict(res.getheaders()), indent=2))
    print("\nResponse Body:")
    print(data.decode("utf-8"))

    # Then test with Instagram URL
    instagram_url = "/scrape?url=https%3A%2F%2Fwww.instagram.com%2Freels%2FDIEj1QZN22_%2F"
    print(f"\nTesting with Instagram URL: {instagram_url}")
    conn.request("GET", instagram_url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print("\nResponse Status:", res.status)
    print("\nResponse Headers:")
    print(json.dumps(dict(res.getheaders()), indent=2))
    print("\nResponse Body:")
    print(data.decode("utf-8"))

if __name__ == "__main__":
    test_scrape_ninja() 