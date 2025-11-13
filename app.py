from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
from urllib.parse import quote
import logging

# WICHTIG: direkt aus dem Builder importieren – inkl. Version für Sichtbarkeit
from pptx_builder import build_pptx, build_base64, sanitize_text, BUILDER_VERSION
from json_sanitizer import validate_and_sanitize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="PPTX Maker")

# CORS (erlaubt Aufrufe aus Power Automate/Browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "pptx-maker",
        "builder_version": BUILDER_VERSION,
        "features": [
            "unicode-sanitization",
            "raw-json-passthrough",
            "json-auto-correction",
            "robustness-layer"
        ]
    }

def _extract_and_sanitize_deck(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and sanitizes deck from payload.
    Uses json_sanitizer for robustness against malformed JSON from LLMs.
    """
    try:
        # Validate and sanitize the entire payload
        sanitized_deck = validate_and_sanitize(payload)

        # Mini-Diagnose: welche Keys kommen pro Slide an?
        slides = sanitized_deck.get("slides", [])
        if isinstance(slides, list):
            for i, sl in enumerate(slides, start=1):
                if isinstance(sl, dict):
                    logger.info(f"Slide {i} keys: {list(sl.keys())}")

        # Builder-Version zusätzlich in meta schreiben (sichtbar im PPTX-Badge & Header)
        meta = sanitized_deck.setdefault("meta", {})
        if isinstance(meta, dict):
            meta.setdefault("builder_version", BUILDER_VERSION)

        return sanitized_deck

    except ValueError as e:
        # Validation error from sanitizer
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected error
        logger.exception("Unexpected error during deck extraction")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/render")
def render_pptx(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Rendert eine PPTX und liefert Base64 + Dateiname.
    Enthält automatische JSON-Korrektur für robuste Verarbeitung von LLM-Output.
    """
    try:
        deck = _extract_and_sanitize_deck(payload)
        customer = sanitize_text(deck.get("meta", {}).get("customer", "Deck"))
        title = sanitize_text(deck.get("meta", {}).get("deckTitle", "Presentation"))
        filename = f"{customer} - {title}.pptx"
        result = build_base64(deck, filename)
        # Optional: Version im Response ergänzen für Debug
        result["_meta"] = {
            "builder_version": deck.get("meta", {}).get("builder_version", BUILDER_VERSION),
            "sanitized": True
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in /render endpoint")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render/bytes")
def render_pptx_bytes(payload: Dict[str, Any] = Body(...)):
    """
    Rendert PPTX und liefert rohe Bytes mit passenden HTTP-Headern.
    Enthält automatische JSON-Korrektur für robuste Verarbeitung von LLM-Output.
    media_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    """
    try:
        deck = _extract_and_sanitize_deck(payload)

        customer = sanitize_text(deck.get("meta", {}).get("customer", "Deck"))
        title = sanitize_text(deck.get("meta", {}).get("deckTitle", "Presentation"))
        filename = f"{customer} - {title}.pptx"

        # URL-encode filename für Content-Disposition (RFC 5987)
        filename_encoded = quote(filename)

        pptx_bytes = build_pptx(deck)

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                # Doppelstrategie: klassisches filename + RFC5987 filename* für saubere Anzeige
                "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{filename_encoded}',
                "X-PPTX-Builder-Version": deck.get("meta", {}).get("builder_version", BUILDER_VERSION),
                "X-PPTX-Sanitized": "true",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in /render/bytes endpoint")
        raise HTTPException(status_code=500, detail=str(e))
