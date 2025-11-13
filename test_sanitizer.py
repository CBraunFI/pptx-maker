"""
Test script to demonstrate JSON sanitizer robustness.
Tests various malformed JSON scenarios that might come from LLMs.
"""
import json
import sys
from json_sanitizer import validate_and_sanitize

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Test Case 1: Missing required fields
print("=" * 60)
print("TEST 1: Missing meta and minimal structure")
print("=" * 60)

test1 = {
    "deck": {
        "slides": [
            {
                "type": "title",
                "title": "Hello World"
            }
        ]
    }
}

try:
    result = validate_and_sanitize(test1)
    print("✓ SUCCESS - Defaults filled in")
    print(f"  Customer: {result['meta']['customer']}")
    print(f"  Title: {result['meta']['deckTitle']}")
    print(f"  Colors: {result['meta']['style']['colors']['primary']}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 2: Invalid color codes
print("\n" + "=" * 60)
print("TEST 2: Invalid hex colors")
print("=" * 60)

test2 = {
    "deck": {
        "meta": {
            "customer": "Test Corp",
            "deckTitle": "My Deck",
            "style": {
                "colors": {
                    "primary": "blue",  # Invalid
                    "accent1": "#GGG",  # Invalid
                    "text": "12345",    # Missing #
                    "background": "#FFF"  # Valid short form
                }
            }
        },
        "slides": []
    }
}

try:
    result = validate_and_sanitize(test2)
    print("✓ SUCCESS - Colors sanitized")
    print(f"  Primary: {result['meta']['style']['colors']['primary']}")
    print(f"  Accent1: {result['meta']['style']['colors']['accent1']}")
    print(f"  Text: {result['meta']['style']['colors']['text']}")
    print(f"  Background: {result['meta']['style']['colors']['background']}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 3: String instead of list
print("\n" + "=" * 60)
print("TEST 3: String content instead of list")
print("=" * 60)

test3 = {
    "deck": {
        "meta": {
            "customer": "ACME",
            "deckTitle": "Presentation"
        },
        "slides": [
            {
                "id": "01",
                "type": "agenda",
                "title": "Agenda",
                "content": "This should be a list"  # String instead of list
            }
        ]
    }
}

try:
    result = validate_and_sanitize(test3)
    print("✓ SUCCESS - String converted to list")
    print(f"  Content type: {type(result['slides'][0]['content'])}")
    print(f"  Content: {result['slides'][0]['content']}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 4: Invalid slide types
print("\n" + "=" * 60)
print("TEST 4: Invalid slide type")
print("=" * 60)

test4 = {
    "deck": {
        "meta": {
            "customer": "Example Inc",
            "deckTitle": "Test"
        },
        "slides": [
            {
                "type": "invalid_type_xyz",  # Invalid
                "title": "My Slide"
            },
            {
                "type": 123,  # Wrong type
                "title": "Another Slide"
            }
        ]
    }
}

try:
    result = validate_and_sanitize(test4)
    print("✓ SUCCESS - Invalid types fixed")
    print(f"  Slide 1 type: {result['slides'][0]['type']}")
    print(f"  Slide 2 type: {result['slides'][1]['type']}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 5: Empty slides array
print("\n" + "=" * 60)
print("TEST 5: Empty slides array")
print("=" * 60)

test5 = {
    "deck": {
        "meta": {
            "customer": "TestCo",
            "deckTitle": "Empty Deck"
        },
        "slides": []  # Empty
    }
}

try:
    result = validate_and_sanitize(test5)
    print("✓ SUCCESS - Default title slide created")
    print(f"  Number of slides: {len(result['slides'])}")
    print(f"  First slide type: {result['slides'][0]['type']}")
    print(f"  First slide title: {result['slides'][0]['title']}")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 6: Dangerous filename characters
print("\n" + "=" * 60)
print("TEST 6: Dangerous filename characters")
print("=" * 60)

test6 = {
    "deck": {
        "meta": {
            "customer": "../../../etc/passwd",  # Path traversal attempt
            "deckTitle": "File<>with|bad?chars*"  # Invalid filename chars
        },
        "slides": [{"type": "title", "title": "Test"}]
    }
}

try:
    result = validate_and_sanitize(test6)
    print("✓ SUCCESS - Dangerous characters removed")
    print(f"  Sanitized customer: '{result['meta']['customer']}'")
    print(f"  Sanitized title: '{result['meta']['deckTitle']}'")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 7: Missing slide IDs and titles
print("\n" + "=" * 60)
print("TEST 7: Missing IDs and titles")
print("=" * 60)

test7 = {
    "deck": {
        "meta": {"customer": "Test", "deckTitle": "Test"},
        "slides": [
            {"type": "text"},  # No ID, no title
            {"type": "agenda"},  # No ID, no title
        ]
    }
}

try:
    result = validate_and_sanitize(test7)
    print("✓ SUCCESS - IDs and titles auto-generated")
    for i, slide in enumerate(result['slides'], 1):
        print(f"  Slide {i}: ID='{slide['id']}', Title='{slide['title']}'")
except Exception as e:
    print(f"✗ FAILED: {e}")

# Test Case 8: Completely broken payload
print("\n" + "=" * 60)
print("TEST 8: Completely broken payload (should fail gracefully)")
print("=" * 60)

test8 = {"not_a_deck": "invalid"}

try:
    result = validate_and_sanitize(test8)
    print("✗ Should have failed but didn't")
except ValueError as e:
    print(f"✓ SUCCESS - Correctly rejected: {e}")
except Exception as e:
    print(f"? Unexpected error: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
