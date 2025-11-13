"""
JSON Sanitizer & Validator for PPTX Maker
Robustness layer to handle imperfect JSON from Copilot/LLM agents
"""
import logging
import re
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Default values
DEFAULT_COLORS = {
    "primary": "#06206F",
    "accent1": "#2FCAC3",
    "accent2": "#966668",
    "text": "#011533",
    "background": "#FFFFFF"
}

VALID_SLIDE_TYPES = {
    "title", "agenda", "context", "need", "understanding", "vision",
    "approach", "principles", "architecture", "modules_overview",
    "module_detail", "transfer", "digital", "coaching", "target_group",
    "impact", "about_synk", "team", "references", "expertise", "partners",
    "investment", "next_steps", "contact"
}


def sanitize_hex_color(color: Any, fallback: str = "#000000") -> str:
    """
    Validates and fixes hex color codes.

    Examples:
        "06206F" -> "#06206F"
        "#GGG" -> fallback
        "blue" -> fallback
    """
    if not isinstance(color, str):
        logger.warning(f"Invalid color type: {type(color)}, using fallback {fallback}")
        return fallback

    # Remove whitespace
    color = color.strip()

    # Add # if missing
    if not color.startswith("#"):
        color = f"#{color}"

    # Validate hex format
    if re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return color.upper()

    # Try to expand 3-char hex to 6-char
    if re.match(r'^#[0-9A-Fa-f]{3}$', color):
        r, g, b = color[1], color[2], color[3]
        expanded = f"#{r}{r}{g}{g}{b}{b}".upper()
        logger.info(f"Expanded short hex {color} to {expanded}")
        return expanded

    logger.warning(f"Invalid hex color '{color}', using fallback {fallback}")
    return fallback


def ensure_list(value: Any, allow_empty: bool = True) -> List[Any]:
    """
    Converts various types to list.

    Examples:
        "text" -> ["text"]
        None -> []
        ["a", "b"] -> ["a", "b"]
    """
    if value is None:
        return [] if allow_empty else [""]

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value] if value.strip() else ([] if allow_empty else [""])

    # Convert other types to string
    return [str(value)]


def sanitize_filename_safe(text: str) -> str:
    """
    Makes text safe for filenames by removing dangerous characters.
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove dangerous characters
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', text)
    text = text.strip('. ')

    # Limit length
    return text[:200] if text else "Document"


def sanitize_slide(slide: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Validates and fixes a single slide object.
    """
    if not isinstance(slide, dict):
        logger.error(f"Slide {index} is not a dict, creating minimal slide")
        return {
            "id": f"slide_{index}",
            "type": "text",
            "title": f"Slide {index}",
            "content": []
        }

    sanitized = slide.copy()

    # Ensure ID
    if "id" not in sanitized or not sanitized["id"]:
        sanitized["id"] = f"slide_{index:02d}"
        logger.info(f"Added missing ID: {sanitized['id']}")

    # Validate and fix type
    slide_type = sanitized.get("type", "")
    if not isinstance(slide_type, str) or slide_type not in VALID_SLIDE_TYPES:
        logger.warning(f"Invalid slide type '{slide_type}' in slide {index}, defaulting to 'text'")
        sanitized["type"] = "text"

    # Ensure title
    if "title" not in sanitized or not sanitized["title"]:
        sanitized["title"] = f"Slide {index}"
        logger.info(f"Added missing title for slide {sanitized['id']}")

    # Normalize content fields based on type
    slide_type = sanitized["type"]

    # For agenda: ensure items or content
    if slide_type == "agenda":
        if "items" not in sanitized and "content" not in sanitized:
            sanitized["content"] = []
            logger.warning(f"Agenda slide {sanitized['id']} has no items/content")

    # For modules_overview: ensure modules list
    if slide_type == "modules_overview":
        if "modules" not in sanitized or not isinstance(sanitized["modules"], list):
            sanitized["modules"] = []
            logger.warning(f"modules_overview slide {sanitized['id']} has no valid modules list")

    # For team: ensure members or trainers
    if slide_type == "team":
        if "members" not in sanitized and "trainers" not in sanitized:
            sanitized["members"] = []
            logger.warning(f"Team slide {sanitized['id']} has no members/trainers")

    # For investment: ensure items
    if slide_type == "investment":
        if "items" not in sanitized or not isinstance(sanitized["items"], list):
            sanitized["items"] = []
            logger.warning(f"Investment slide {sanitized['id']} has no items")

    # For contact: ensure contact dict
    if slide_type == "contact":
        if "contact" not in sanitized or not isinstance(sanitized["contact"], dict):
            sanitized["contact"] = {
                "name": "Contact Person",
                "email": "contact@example.com"
            }
            logger.warning(f"Contact slide {sanitized['id']} has no valid contact dict")

    # Normalize content/text/bullets/items
    # Convert single strings to lists where appropriate
    for key in ["content", "items", "bullets"]:
        if key in sanitized and isinstance(sanitized[key], str):
            sanitized[key] = [sanitized[key]]
            logger.info(f"Converted {key} from string to list in slide {sanitized['id']}")

    return sanitized


def sanitize_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and fixes meta section with defaults.
    """
    if not isinstance(meta, dict):
        logger.error("Meta is not a dict, using defaults")
        meta = {}

    sanitized = {
        "deckTitle": meta.get("deckTitle") or "Presentation",
        "deckSubtitle": meta.get("deckSubtitle", ""),
        "author": meta.get("author") or "SYNK GROUP",
        "date": meta.get("date") or "2025-01-01",
        "customer": meta.get("customer") or "Client",
        "useCase": meta.get("useCase", "")
    }

    # Sanitize filenames for customer and title
    sanitized["customer"] = sanitize_filename_safe(sanitized["customer"])
    sanitized["deckTitle"] = sanitize_filename_safe(sanitized["deckTitle"])

    # Handle style
    style = meta.get("style", {})
    if not isinstance(style, dict):
        logger.warning("Style is not a dict, using defaults")
        style = {}

    # Handle colors
    colors = style.get("colors", {})
    if not isinstance(colors, dict):
        logger.warning("Colors is not a dict, using defaults")
        colors = {}

    sanitized_colors = {}
    for color_key, default_value in DEFAULT_COLORS.items():
        color_value = colors.get(color_key, default_value)
        sanitized_colors[color_key] = sanitize_hex_color(color_value, default_value)

    sanitized["style"] = {
        "font": style.get("font") or "Arial",
        "colors": sanitized_colors,
        "logo": style.get("logo", ""),
        "clientLogo": style.get("clientLogo", "")
    }

    return sanitized


def sanitize_deck(payload: Any) -> Dict[str, Any]:
    """
    Main sanitization function: validates and fixes the entire deck structure.

    Args:
        payload: Raw input (should contain "deck" key)

    Returns:
        Sanitized deck dict ready for pptx_builder

    Raises:
        ValueError: If payload is completely invalid
    """
    logger.info("=== Starting JSON Sanitization ===")

    # Check if payload is a dict
    if not isinstance(payload, dict):
        logger.error(f"Payload is not a dict: {type(payload)}")
        raise ValueError(f"Payload must be a dictionary, got {type(payload)}")

    # Extract deck
    if "deck" not in payload:
        logger.error("Missing 'deck' key in payload")
        raise ValueError("Payload must contain a 'deck' key")

    deck = payload["deck"]
    if not isinstance(deck, dict):
        logger.error(f"Deck is not a dict: {type(deck)}")
        raise ValueError(f"Deck must be a dictionary, got {type(deck)}")

    # Sanitize meta
    logger.info("Sanitizing meta section...")
    sanitized_meta = sanitize_meta(deck.get("meta", {}))

    # Sanitize slides
    slides = deck.get("slides", [])
    if not isinstance(slides, list):
        logger.warning(f"Slides is not a list: {type(slides)}, converting to empty list")
        slides = []

    if len(slides) == 0:
        logger.warning("No slides found, creating default title slide")
        slides = [{
            "id": "01",
            "type": "title",
            "title": sanitized_meta["deckTitle"],
            "subtitle": sanitized_meta["deckSubtitle"]
        }]

    logger.info(f"Sanitizing {len(slides)} slides...")
    sanitized_slides = []
    for i, slide in enumerate(slides, start=1):
        sanitized_slide = sanitize_slide(slide, i)
        sanitized_slides.append(sanitized_slide)

    sanitized_deck = {
        "meta": sanitized_meta,
        "slides": sanitized_slides
    }

    logger.info(f"=== Sanitization complete: {len(sanitized_slides)} slides validated ===")

    return sanitized_deck


def validate_and_sanitize(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public API: Validates and sanitizes a complete payload.

    Usage:
        from json_sanitizer import validate_and_sanitize

        try:
            clean_deck = validate_and_sanitize(raw_payload)
            pptx_bytes = build_pptx(clean_deck)
        except ValueError as e:
            # Handle validation error
            pass
    """
    return sanitize_deck(payload)
