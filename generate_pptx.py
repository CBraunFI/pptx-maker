import json
import sys
from pptx_builder import build_pptx

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load the JSON input
with open('input_leadership.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract deck data
deck = data['deck']

# Generate the PPTX
print(f"Generating presentation: {deck['meta']['deckTitle']}")
print(f"Customer: {deck['meta']['customer']}")
print(f"Slides: {len(deck['slides'])}")

pptx_bytes = build_pptx(deck)

# Save to file
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{deck['meta']['customer']} - {deck['meta']['deckTitle']} - {timestamp}.pptx"
with open(filename, 'wb') as f:
    f.write(pptx_bytes)

print(f"\n✓ Successfully created: {filename}")
print(f"  Size: {len(pptx_bytes):,} bytes")
print(f"  Location: {filename}")
