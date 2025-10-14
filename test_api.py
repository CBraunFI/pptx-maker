import requests
import json
import base64
import time
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("Testing GET / ...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ Root endpoint works\n")

def test_render_simple():
    """Test rendering a simple presentation"""
    print("Testing POST /render with simple deck...")

    payload = {
        "deck": {
            "meta": {
                "deckTitle": "Test Presentation",
                "deckSubtitle": "A test subtitle",
                "author": "Test Author",
                "date": "2025-10-14",
                "customer": "Test Customer",
                "style": {
                    "font": "Arial Narrow",
                    "colors": {
                        "primary": "#1E3A8A",
                        "accent1": "#3B82F6",
                        "text": "#1F2937"
                    }
                }
            },
            "slides": [
                {
                    "id": "slide1",
                    "type": "title",
                    "title": "Welcome to Test Presentation",
                    "subtitle": "Testing the PPTX Maker Service"
                },
                {
                    "id": "slide2",
                    "type": "context",
                    "title": "Context",
                    "content": ["This is a test slide", "With multiple bullet points", "To verify functionality"]
                }
            ]
        }
    }

    response = requests.post(f"{BASE_URL}/render", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Filename: {data['filename']}")
        print(f"Base64 length: {len(data['file'])} characters")

        # Save the file to verify it's valid
        pptx_data = base64.b64decode(data['file'])
        filename = "test_output.pptx"
        with open(filename, "wb") as f:
            f.write(pptx_data)
        print(f"✓ File saved as {filename} ({len(pptx_data)} bytes)")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200

def test_render_complex():
    """Test rendering with all slide types"""
    print("Testing POST /render with complex deck...")

    payload = {
        "deck": {
            "meta": {
                "deckTitle": "Complex Test Deck",
                "deckSubtitle": "Testing all features",
                "author": "Test Suite",
                "date": "2025-10-14",
                "customer": "QA Team",
                "style": {
                    "font": "Arial Narrow",
                    "colors": {
                        "primary": "#DC2626",
                        "accent1": "#EF4444",
                        "text": "#111827"
                    }
                }
            },
            "slides": [
                {
                    "id": "s1",
                    "type": "title",
                    "title": "Complex Presentation Test"
                },
                {
                    "id": "s2",
                    "type": "modules_overview",
                    "title": "Modules Overview",
                    "modules": [
                        {"title": "Module 1", "duration": "2h"},
                        {"title": "Module 2", "duration": "3h"}
                    ]
                },
                {
                    "id": "s3",
                    "type": "team",
                    "title": "Our Team",
                    "trainers": [
                        {"name": "John Doe", "role": "Lead Trainer"},
                        {"name": "Jane Smith", "role": "Co-Trainer"}
                    ]
                },
                {
                    "id": "s4",
                    "type": "investment",
                    "title": "Investment",
                    "content": [
                        "Basic Package – €1,000",
                        "Premium Package – €2,500"
                    ]
                }
            ]
        }
    }

    response = requests.post(f"{BASE_URL}/render", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Filename: {data['filename']}")
        pptx_data = base64.b64decode(data['file'])
        filename = "test_output_complex.pptx"
        with open(filename, "wb") as f:
            f.write(pptx_data)
        print(f"✓ Complex file saved as {filename} ({len(pptx_data)} bytes)")
    else:
        print(f"✗ Error: {response.text}")

    print()
    return response.status_code == 200

def test_invalid_color():
    """Test with invalid color format"""
    print("Testing with invalid color format...")

    payload = {
        "deck": {
            "meta": {
                "deckTitle": "Bad Color Test",
                "author": "Test",
                "date": "2025-10-14",
                "customer": "Test",
                "style": {
                    "font": "Arial",
                    "colors": {
                        "primary": "invalid",
                        "accent1": "#FF0000",
                        "text": "#000000"
                    }
                }
            },
            "slides": [
                {"id": "s1", "type": "title", "title": "Test"}
            ]
        }
    }

    response = requests.post(f"{BASE_URL}/render", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    print()

def test_missing_fields():
    """Test with missing required fields"""
    print("Testing with missing required fields...")

    payload = {
        "deck": {
            "meta": {
                "deckTitle": "Test"
                # Missing required fields
            },
            "slides": []
        }
    }

    response = requests.post(f"{BASE_URL}/render", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("PPTX Maker API Test Suite")
    print("=" * 60)
    print()

    # Wait a bit for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)

    try:
        test_root()
        test_render_simple()
        test_render_complex()
        test_invalid_color()
        test_missing_fields()

        print("=" * 60)
        print("Test suite completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
