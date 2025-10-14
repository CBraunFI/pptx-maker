import requests
import json

# Test the /render/bytes endpoint
url = "http://localhost:8000/render/bytes"

# Simple test payload
payload = {
    "deck": {
        "meta": {
            "deckTitle": "Test Bytes Endpoint",
            "author": "Test",
            "date": "2025-10-14",
            "customer": "Test Company",
            "style": {
                "font": "Arial",
                "colors": {
                    "primary": "#06206F",
                    "accent1": "#2FCAC3",
                    "text": "#011533"
                },
                "logo": "SYNK-Logo.PNG"
            }
        },
        "slides": [
            {
                "id": "1",
                "type": "title",
                "title": "Test Presentation",
                "subtitle": "Testing Bytes Endpoint"
            },
            {
                "id": "2",
                "type": "agenda",
                "title": "Agenda",
                "content": ["Item 1", "Item 2", "Item 3"]
            }
        ]
    }
}

print("Testing POST /render/bytes endpoint...")
print(f"Sending request to {url}")

response = requests.post(url, json=payload)

print(f"\nStatus Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
print(f"Content Length: {len(response.content)} bytes")

if response.status_code == 200:
    # Save the file directly
    filename = "test_bytes_output.pptx"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"\n✓ File saved as {filename}")
    print(f"  No base64 decoding needed!")
else:
    print(f"\n✗ Error: {response.text}")
