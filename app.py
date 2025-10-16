from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
from urllib.parse import quote
import logging

# WICHTIG: direkt aus dem Builder importieren – inkl. Version für Sichtbarkeit
from pptx_builder import build_pptx, build_base64, sanitize_text, BUILDER_VERSION

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
        "features": ["unicode-sanitization", "raw-json-passthrough"]
    }

def _extract_deck(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or "deck" not in payload:
        raise HTTPException(status_code=400, detail="Request body must contain a top-level 'deck' object.")
    deck = payload["deck"]
    if not isinstance(deck, dict):
        raise HTTPException(status_code=400, detail="'deck' must be an object.")
    # Mini-Diagnose: welche Keys kommen pro Slide an?
    slides = deck.get("slides", [])
    if isinstance(slides, list):
        for i, sl in enumerate(slides, start=1):
            if isinstance(sl, dict):
                logging.info("pptx-maker: slide %s keys -> %s", i, list(sl.keys()))
    # Builder-Version zusätzlich in meta schreiben (sichtbar im PPTX-Badge & Header)
    meta = deck.setdefault("meta", {})
    if isinstance(meta, dict):
        meta.setdefault("builder_version", BUILDER_VERSION)
    return deck

@app.post("/render")
def render_pptx(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Rendert eine PPTX und liefert Base64 + Dateiname (kompatibel zu deiner bisherigen /render-Nutzung).
    Keine Pydantic-Modelle -> keine Felder werden „abgeschnitten“.
    """
    try:
        deck = _extract_deck(payload)
        customer = sanitize_text(deck.get("meta", {}).get("customer", "Deck"))
        title = sanitize_text(deck.get("meta", {}).get("deckTitle", "Presentation"))
        filename = f"{customer} - {title}.pptx"
        result = build_base64(deck, filename)
        # Optional: Version im Response ergänzen für Debug
        result["_meta"] = {"builder_version": deck.get("meta", {}).get("builder_version", BUILDER_VERSION)}
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("pptx-maker /render error")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render/bytes")
def render_pptx_bytes(payload: Dict[str, Any] = Body(...)):
    """
    Rendert PPTX und liefert rohe Bytes mit passenden HTTP-Headern.
    media_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    """
    try:
        deck = _extract_deck(payload)

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
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("pptx-maker /render/bytes error")
        raise HTTPException(status_code=500, detail=str(e))
