# PPTX Maker API - Copilot Agent Guide

## Overview
The PPTX Maker is a FastAPI service that generates professional PowerPoint presentations from structured JSON input. It creates 16:9 presentations with custom branding, colors, and dual-logo support.

---

## API Endpoints

### 1. Health Check
```
GET /
```
**Response:**
```json
{
  "status": "ok",
  "service": "pptx-maker"
}
```

### 2. Render Presentation (Base64)
```
POST /render
Content-Type: application/json
```

**Request Body:** JSON object with presentation structure (see below)

**Response:**
```json
{
  "filename": "Customer Name - Presentation Title.pptx",
  "file": "base64_encoded_pptx_data..."
}
```

**Note:** Returns base64-encoded PPTX file. Requires decoding before saving.

### 3. Render Presentation (Raw Bytes) ⭐ RECOMMENDED
```
POST /render/bytes
Content-Type: application/json
```

**Request Body:** Same JSON structure as `/render`

**Response:**
- **Content-Type:** `application/vnd.openxmlformats-officedocument.presentationml.presentation`
- **Content-Disposition:** `attachment; filename="Customer - Title.pptx"`
- **Body:** Raw PPTX file bytes (binary)

**Advantages:**
- No base64 encoding/decoding needed
- Smaller payload size (~25% smaller than base64)
- Direct file download in browsers
- Faster processing
- Simpler integration

---

## JSON Structure Reference

### Complete JSON Schema

```json
{
  "deck": {
    "meta": {
      "deckTitle": "string (required)",
      "deckSubtitle": "string (optional)",
      "author": "string (required)",
      "date": "string (required, format: YYYY-MM-DD)",
      "customer": "string (required)",
      "useCase": "string (optional)",
      "style": {
        "font": "string (default: 'Arial Narrow')",
        "colors": {
          "primary": "string (hex color, e.g., '#06206F')",
          "accent1": "string (hex color)",
          "accent2": "string (optional, hex color)",
          "text": "string (hex color)",
          "background": "string (optional, hex color)"
        },
        "logo": "string (optional, filename of SYNK logo)",
        "clientLogo": "string (optional, filename of client logo)"
      }
    },
    "slides": [
      {
        "id": "string (required, unique identifier)",
        "type": "string (required, see Slide Types below)",
        "title": "string (required)",
        "subtitle": "string (optional)",
        "content": "string or array of strings (optional)",
        "modules": "array of ModuleItem (optional, for modules_overview)",
        "trainers": "array of TrainerItem (optional, for team slides)",
        "visual": "string (optional, hint for visual elements)",
        "designHint": "string (optional, design guidance)"
      }
    ]
  }
}
```

---

## Slide Types

The following slide types are supported. Each type has specific rendering behavior:

### Basic Content Slides
- **`title`** - Title slide with dark background, no logos
- **`agenda`** - Agenda/overview slide with bullet points
- **`context`** - Context/background information
- **`need`** - Problem statement or needs
- **`understanding`** - Understanding/insights
- **`vision`** - Vision or goals
- **`approach`** - Approach or methodology
- **`principles`** - Principles or guidelines
- **`architecture`** - Architecture overview
- **`transfer`** - Transfer or implementation
- **`digital`** - Digital solutions
- **`coaching`** - Coaching information
- **`target_group`** - Target audience
- **`impact`** - Impact or results
- **`about_synk`** - About SYNK company info
- **`references`** - Client references
- **`expertise`** - Expertise areas
- **`partners`** - Partners and networks
- **`next_steps`** - Next steps or roadmap
- **`contact`** - Contact information

### Special Slides
- **`modules_overview`** - Table of training modules
  - Requires: `modules` array with ModuleItem objects

- **`module_detail`** - Detailed module information
  - Header prefix: "Modul"

- **`team`** - Team members presentation
  - Requires: `trainers` array with TrainerItem objects
  - Formats as "Name – Role"

- **`investment`** - Pricing/investment table
  - Content format: "Option – Price" (separated by en-dash)
  - Renders as 3-column table: Option | Service/Note | Price

---

## Data Types

### ModuleItem
```json
{
  "title": "string (required)",
  "duration": "string (optional, e.g., '2h', '1 Tag')",
  "outcomes": "array of strings (optional)"
}
```

### TrainerItem
```json
{
  "name": "string (required)",
  "role": "string (required)",
  "bio": "string (optional)",
  "photoRef": "string (optional)"
}
```

---

## Logo Configuration

### SYNK Logo (Bottom Right)
- **Position:** Bottom right corner
- **Size:** 0.4" height (maintains aspect ratio)
- **Margins:** 0.3" from right, 0.2" from bottom
- **Field:** `deck.meta.style.logo`
- **Supported formats:** PNG, JPG, JPEG (case-insensitive)

### Client Logo (Bottom Left)
- **Position:** Bottom left corner
- **Size:** 0.4" height (maintains aspect ratio)
- **Margins:** 0.3" from left, 0.2" from bottom
- **Field:** `deck.meta.style.clientLogo`
- **Supported formats:** PNG, JPG, JPEG (case-insensitive)

### Logo Behavior
- **Title slide (first slide):** No logos displayed
- **All other slides:** Both logos displayed (if provided)
- **Missing logos:** Service continues without error
- **Auto-detection:** Tries multiple file extensions automatically

---

## Presentation Specifications

### Slide Format
- **Aspect Ratio:** 16:9
- **Dimensions:** 10" × 5.625"

### Typography
- **Default Font:** Arial (applied throughout)
- **Title Slide:**
  - Title: 44pt, Bold, White
  - Subtitle: 20pt, White
- **Content Slides:**
  - Headers: 28pt, Bold
  - Body text: 20pt
- **Tables:**
  - Headers: Bold, accent color background
  - Body: Standard weight

### Colors
All colors must be provided as hex codes (e.g., `#06206F`).

**Standard SYNK Color Palette:**
```json
{
  "primary": "#06206F",    // Dark blue (backgrounds)
  "accent1": "#2FCAC3",    // Turquoise (accents, tables)
  "accent2": "#966668",    // Rose (optional accent)
  "text": "#011533",       // Dark text
  "background": "#FFFFFF"  // White background
}
```

### Layout
- **Margins:** 0.5" on all sides
- **Header area:** 0.5" from top, 0.6" high
- **Body area:** 1.3" from top, 3.8" high
- **Logo area:** Bottom 0.6" reserved for logos

---

## Example JSON Payload

### Minimal Example
```json
{
  "deck": {
    "meta": {
      "deckTitle": "Leadership Journey 2026",
      "author": "SYNK GROUP GmbH & Co. KG",
      "date": "2025-10-14",
      "customer": "Muster AG",
      "style": {
        "font": "Arial",
        "colors": {
          "primary": "#06206F",
          "accent1": "#2FCAC3",
          "text": "#011533"
        },
        "logo": "SYNK-Logo.PNG",
        "clientLogo": "Muster-AG-Logo.png"
      }
    },
    "slides": [
      {
        "id": "01",
        "type": "title",
        "title": "Leadership Journey 2026",
        "subtitle": "Muster AG × SYNK GROUP"
      },
      {
        "id": "02",
        "type": "agenda",
        "title": "Agenda",
        "content": [
          "Ausgangslage & Zielsetzung",
          "Unser Ansatz & Programmdesign",
          "Module & Transfer"
        ]
      }
    ]
  }
}
```

### Modules Overview Example
```json
{
  "id": "10",
  "type": "modules_overview",
  "title": "Module im Überblick",
  "modules": [
    {
      "title": "M1: Selbstführung",
      "duration": "1 Tag"
    },
    {
      "title": "M2: Teamführung",
      "duration": "2 Tage"
    }
  ]
}
```

### Team Slide Example
```json
{
  "id": "18",
  "type": "team",
  "title": "Unser Team",
  "trainers": [
    {
      "name": "Dr. Jana Müller",
      "role": "Leadership Coach",
      "bio": "Systemische Führung & Kommunikation."
    },
    {
      "name": "Christophe Braun",
      "role": "Head of Product Development",
      "bio": "KI-gestützte Lernlösungen."
    }
  ]
}
```

### Investment Slide Example
```json
{
  "id": "22",
  "type": "investment",
  "title": "Investition",
  "content": [
    "Option A: 3 Module à 1 Tag – 18.500 €",
    "Option B: 2 Module + Coaching – 14.900 €"
  ]
}
```

---

## Content Guidelines

### Text Content
- **Bullet points:** Use array of strings for `content` field
- **Paragraphs:** Use single string for `content` field
- **Word wrap:** Enabled automatically
- **Special characters:** UTF-8 supported (ä, ö, ü, ß, €, etc.)

### Character Encoding Best Practices

**IMPORTANT: The API automatically sanitizes Unicode characters to prevent encoding errors.**

To ensure maximum compatibility, **avoid** using the following Unicode characters in your JSON:

❌ **Characters to AVOID:**
- Em-dash: `–` (U+2013) → Use regular hyphen `-` instead
- En-dash: `—` (U+2014) → Use regular hyphen `-` instead
- Smart quotes: `"` `"` (U+201C, U+201D) → Use straight quotes `"` instead
- Smart single quotes: `'` `'` (U+2018, U+2019) → Use straight apostrophe `'` instead
- Ellipsis: `…` (U+2026) → Use three periods `...` instead
- Non-breaking space: ` ` (U+00A0) → Use regular space instead

✅ **Safe Characters:**
- Regular hyphen: `-`
- Straight quotes: `"` and `'`
- Regular space: ` `
- Three periods: `...`
- German umlauts: `ä`, `ö`, `ü`, `ß`
- Common symbols: `€`, `@`, `&`, `%`

**Example - WRONG:**
```json
{
  "title": "Leadership Journey – 2026",
  "content": "We're ready… let's begin!"
}
```

**Example - CORRECT:**
```json
{
  "title": "Leadership Journey - 2026",
  "content": "We're ready... let's begin!"
}
```

**Note:** The API will automatically convert problematic Unicode characters to ASCII equivalents, but it's best practice to use ASCII-safe characters from the start to avoid any potential data loss.

### Content Length Recommendations
- **Title:** Max 60 characters
- **Subtitle:** Max 80 characters
- **Header:** Max 100 characters
- **Bullet points:** 5-7 bullets per slide recommended
- **Bullet text:** Max 100 characters per bullet

---

## Error Handling

### Common Errors

**400 Bad Request**
- Missing required fields
- Invalid slide type
- Malformed JSON

**422 Unprocessable Entity**
- Invalid data types
- Missing nested required fields

**500 Internal Server Error**
- Invalid color format (not hex)
- File system errors
- Rendering errors
- ~~Unicode encoding errors (FIXED: Now automatically sanitized)~~

### Validation Requirements
1. All required fields must be present
2. Colors must be valid hex codes (e.g., `#RRGGBB`)
3. Dates should follow ISO format (YYYY-MM-DD)
4. Slide IDs must be unique within a deck
5. Slide type must be one of the supported types
6. **Use ASCII-safe characters** (no Em-dashes, smart quotes, etc.)

---

## Response Handling

### Success Response
```json
{
  "filename": "Muster AG - Leadership Journey 2026.pptx",
  "file": "UEsDBBQABgAIAAAAIQD..."
}
```

The `file` field contains the complete PPTX file as base64-encoded string.

### Using /render/bytes (Recommended)
**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:8000/render/bytes',
    json=payload
)

# Save directly - no decoding needed!
filename = response.headers['Content-Disposition'].split('filename=')[1].strip('"')
with open(filename, 'wb') as f:
    f.write(response.content)
```

**JavaScript/Browser Example:**
```javascript
const response = await fetch('http://localhost:8000/render/bytes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

// Create download link directly
const blob = await response.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'presentation.pptx';
a.click();
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/render/bytes \
  -H "Content-Type: application/json" \
  -d @payload.json \
  -o output.pptx
```

### Using /render (Base64 - Legacy)
To save the file from base64:
1. Decode the base64 string
2. Write binary data to a `.pptx` file

**Python Example:**
```python
import base64
import requests

response = requests.post('http://localhost:8000/render', json=payload)
data = response.json()

file_data = base64.b64decode(data["file"])
with open(data["filename"], "wb") as f:
    f.write(file_data)
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/render', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

const data = await response.json();
const blob = new Blob(
  [Uint8Array.from(atob(data.file), c => c.charCodeAt(0))],
  { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' }
);
```

---

## Best Practices for Copilot Agents

### 1. Building Presentations
- Always include at least a title slide
- Use consistent color schemes
- Provide clear, concise content
- Follow the 5-7 bullets per slide guideline
- Use appropriate slide types for content

### 2. Content Structure
- **Title Slide:** Company branding, main title
- **Agenda:** 3-5 main points
- **Content Slides:** Focus on one idea per slide
- **Closing Slides:** Contact, next steps

### 3. Color Selection
- Use high contrast for readability
- Dark backgrounds with white text for title slides
- Light backgrounds with dark text for content slides
- Consistent accent colors throughout

### 4. Logo Files
- Ensure logo files exist before referencing
- Use PNG format with transparent backgrounds
- Verify filenames match exactly (case-sensitive on some systems)
- Place logo files in the application directory

### 5. Character Encoding
- **Always use ASCII-safe characters** in all text fields
- Replace Em-dashes `–` with regular hyphens `-`
- Replace smart quotes `"` `'` with straight quotes `"` `'`
- Replace ellipsis `…` with three periods `...`
- The API will sanitize Unicode automatically, but prevention is better

### 6. Error Recovery
- Validate JSON before sending
- Check all required fields are present
- Verify color format (# + 6 hex digits)
- Handle API errors gracefully

---

## Technical Details

### Server Configuration
- **Default Host:** `0.0.0.0` (all interfaces)
- **Default Port:** `8000`
- **CORS:** Enabled for all origins (development mode)
- **Framework:** FastAPI with Uvicorn

### Dependencies
- `fastapi==0.115.0`
- `uvicorn[standard]==0.30.6`
- `python-pptx==0.6.23`
- `pydantic==2.9.2`

### File System Requirements
- Write access to application directory
- Logo files must be in same directory as application
- Generated files saved with timestamp to avoid conflicts

---

## Workflow Example for Copilot Agent

### Step 1: Gather Information
Ask user for:
- Presentation title and customer name
- Number and types of slides needed
- Content for each slide
- Preferred color scheme
- Client logo file (if available)

### Step 2: Build JSON Structure
```json
{
  "deck": {
    "meta": { /* metadata */ },
    "slides": [ /* slide array */ ]
  }
}
```

### Step 3: Send API Request (Use Bytes Endpoint)
```http
POST http://localhost:8000/render/bytes
Content-Type: application/json

{JSON payload}
```

### Step 4: Process Response
- Receive raw PPTX bytes (no decoding needed!)
- Save directly as .pptx file
- Provide download link to user

**Alternative (Legacy):**
- Use `/render` for base64 response
- Decode base64 to binary
- Save as .pptx file

### Step 5: Handle Errors
- Check response status code
- Parse error details
- Provide user-friendly error messages
- Suggest corrections

---

## Quick Reference: Slide Type Selection Guide

| Content Type | Slide Type | Special Fields |
|--------------|------------|----------------|
| Cover/Title | `title` | subtitle |
| Table of contents | `agenda` | content (array) |
| Background info | `context` | content |
| Problem statement | `need` | content (array) |
| Analysis | `understanding` | content |
| Goals | `vision` | content |
| Method | `approach` | content (array) |
| Guidelines | `principles` | content (array) |
| System design | `architecture` | content, visual |
| Training modules table | `modules_overview` | modules (array) |
| Single module detail | `module_detail` | content |
| Implementation | `transfer` | content (array) |
| Digital tools | `digital` | content |
| Coaching info | `coaching` | content |
| Audience | `target_group` | content (array) |
| Results/metrics | `impact` | content, visual |
| Company profile | `about_synk` | content |
| Team members | `team` | trainers (array) |
| Client logos/names | `references` | content (array) |
| Competencies | `expertise` | content (array) |
| Partnerships | `partners` | content (array) |
| Pricing table | `investment` | content (array with –) |
| Timeline/roadmap | `next_steps` | content (array), visual |
| Contact details | `contact` | content |

---

## Support & Troubleshooting

### Common Issues

**"Invalid color format" error:**
- Ensure colors start with `#`
- Use 6-digit hex codes (e.g., `#06206F`)
- Avoid 3-digit shorthand

**"File not found" for logos:**
- Verify logo file exists in application directory
- Check filename spelling and case
- Try with and without file extension in JSON

**Empty slides:**
- Check content field is properly formatted
- Use array for multiple items
- Use string for single paragraph

**Text overflow:**
- Reduce content length
- Split into multiple slides
- Use shorter bullet points

**"Unicode/latin-1 encoding" errors (legacy):**
- This should no longer occur (fixed in v1.1)
- If you encounter this, the API auto-sanitizes problematic characters
- For best results, use ASCII-safe characters (see Character Encoding Best Practices above)

---

## Version Information

- **API Version:** 1.1
- **Slide Format:** 16:9 (10" × 5.625")
- **Font:** Arial
- **Logo Support:** Dual logos (SYNK + Client)
- **Unicode Handling:** Automatic sanitization (v1.1+)
- **Last Updated:** 2025-10-14

### Changelog

**v1.1 (2025-10-14)**
- ✅ Added automatic Unicode character sanitization
- ✅ Fixed latin-1 encoding errors with Em-dashes, smart quotes, etc.
- ✅ Improved Power Automate compatibility
- ℹ️ API now auto-converts problematic Unicode to ASCII equivalents

**v1.0 (2025-10-14)**
- Initial release
- 24 slide types
- Dual logo support
- Base64 and bytes endpoints

---

## Contact & Resources

- **Service Name:** PPTX Maker
- **Framework:** FastAPI + python-pptx
- **Health Check:** `GET /`
- **Main Endpoint:** `POST /render`

For questions or issues with the PPTX Maker API, refer to this guide or check the API health endpoint.