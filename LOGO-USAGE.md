# Logo Usage Guide

## Logo Positioning

The PPTX Maker now supports dual logos on all slides except the title slide:

### SYNK Logo (Bottom Right)
- **Position**: Bottom right corner
- **Size**: 0.4" height (maintains aspect ratio)
- **Margin**: 0.3" from right edge, 0.2" from bottom
- **JSON field**: `deck.meta.style.logo`

### Client Logo (Bottom Left)
- **Position**: Bottom left corner
- **Size**: 0.4" height (maintains aspect ratio)
- **Margin**: 0.3" from left edge, 0.2" from bottom
- **JSON field**: `deck.meta.style.clientLogo`

## JSON Structure

```json
{
  "deck": {
    "meta": {
      "style": {
        "logo": "SYNK-Logo.PNG",
        "clientLogo": "Client-Logo.png",
        "font": "Arial Narrow",
        "colors": {
          "primary": "#06206F",
          "accent1": "#2FCAC3",
          "text": "#011533"
        }
      }
    }
  }
}
```

## Logo Requirements

- **Formats**: PNG, JPG, JPEG (case-insensitive)
- **Recommendation**: PNG with transparent background
- **Location**: Place logo files in the same directory as the script
- **Naming**: Use exact filename from JSON (script will try different extensions)

## Behavior

- **Title Slide (Slide 1)**: No logos displayed
- **All Other Slides**: Both SYNK and client logos displayed (if provided)
- **Missing Logos**: If a logo file is not found, the presentation continues without error
- **Auto-detection**: Script automatically tries .png, .PNG, .jpg, .JPG, .jpeg, .JPEG extensions

## Example

For a client "Muster AG", you might have:
- `SYNK-Logo.PNG` (SYNK logo)
- `Muster-AG-Logo.png` (client logo)

In the JSON:
```json
"style": {
  "logo": "SYNK-Logo.PNG",
  "clientLogo": "Muster-AG-Logo.png"
}
```
