from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from models import RenderRequest, RenderResponse
from pptx_builder import build_base64, build_pptx

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
    return {"status": "ok", "service": "pptx-maker"}

@app.post("/render", response_model=RenderResponse)
def render_pptx(req: RenderRequest):
    try:
        customer = req.deck.meta.customer
        title = req.deck.meta.deckTitle
        filename = f"{customer} - {title}.pptx"
        result = build_base64(req.deck.model_dump(), filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render/bytes")
def render_pptx_bytes(req: RenderRequest):
    """
    Render PPTX and return raw bytes directly.
    Response will be application/vnd.openxmlformats-officedocument.presentationml.presentation
    """
    try:
        customer = req.deck.meta.customer
        title = req.deck.meta.deckTitle
        filename = f"{customer} - {title}.pptx"
        pptx_bytes = build_pptx(req.deck.model_dump())

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
