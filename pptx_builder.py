import io, base64
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from typing import List, Union

def hex_to_rgb(hexstr: str):
    hexstr = hexstr.lstrip("#")
    return RGBColor(int(hexstr[0:2],16), int(hexstr[2:4],16), int(hexstr[4:6],16))

def add_logos(slide, synk_logo_path, client_logo_path, slide_width, slide_height):
    """Add SYNK logo to bottom right and client logo to bottom left of a slide"""
    # SYNK logo - bottom right corner
    if synk_logo_path and os.path.exists(synk_logo_path):
        logo_height = Inches(0.4)
        logo_width = Inches(1.2)  # Approximate width, will maintain aspect ratio
        left = slide_width - logo_width - Inches(0.3)
        top = slide_height - logo_height - Inches(0.2)
        try:
            slide.shapes.add_picture(synk_logo_path, left, top, height=logo_height)
        except Exception as e:
            # If logo fails to load, continue without it
            pass

    # Client logo - bottom left corner
    if client_logo_path and os.path.exists(client_logo_path):
        logo_height = Inches(0.4)
        left = Inches(0.3)
        top = slide_height - logo_height - Inches(0.2)
        try:
            slide.shapes.add_picture(client_logo_path, left, top, height=logo_height)
        except Exception as e:
            # If logo fails to load, continue without it
            pass

def add_title_slide(prs, meta, slide):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    # background (primary)
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(meta["style"]["colors"]["primary"])
    # title
    tb = s.shapes.add_textbox(Inches(1), Inches(1.7), prs.slide_width - Inches(2), Inches(1.2))
    p = tb.text_frame.paragraphs[0]
    p.text = slide["title"]
    p.font.name = "Arial"; p.font.size = Pt(44); p.font.bold = True; p.font.color.rgb = RGBColor(255,255,255)
    tb.text_frame.word_wrap = True
    # subtitle
    sub = s.shapes.add_textbox(Inches(1), Inches(2.7), prs.slide_width - Inches(2), Inches(0.8))
    sp = sub.text_frame.paragraphs[0]
    sp.text = slide.get("subtitle") or (meta["deckSubtitle"] or "")
    sp.font.name = "Arial"; sp.font.size = Pt(20); sp.font.color.rgb = RGBColor(255,255,255)
    sub.text_frame.word_wrap = True
    return s

def add_text_slide(prs, meta, slide, header="", synk_logo_path=None, client_logo_path=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    # Add logos if available
    add_logos(s, synk_logo_path, client_logo_path, prs.slide_width, prs.slide_height)
    # header - fit within 10" slide width with margins
    hdr = s.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9.0), Inches(0.6))
    hp = hdr.text_frame.paragraphs[0]
    hp.text = slide["title"] if not header else header + " – " + slide["title"]
    hp.font.name = "Arial"; hp.font.size = Pt(28); hp.font.bold = True
    hp.font.color.rgb = hex_to_rgb(meta["style"]["colors"]["text"])
    hdr.text_frame.word_wrap = True
    # body - fit within 10" slide width with margins
    left, top, width, height = Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8)
    tb = s.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.clear()
    tf.word_wrap = True
    content = slide.get("content")
    if isinstance(content, list):
        for i, item in enumerate(content):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = item; p.font.name = "Arial"; p.font.size = Pt(20)
            p.font.color.rgb = hex_to_rgb(meta["style"]["colors"]["text"])
    elif isinstance(content, str):
        p = tf.paragraphs[0]
        p.text = content; p.font.name = "Arial"; p.font.size = Pt(20)
        p.font.color.rgb = hex_to_rgb(meta["style"]["colors"]["text"])
    else:
        tf.paragraphs[0].text = ""
    return s

def add_table_slide(prs, meta, slide, headers: List[str], rows: List[List[str]], synk_logo_path=None, client_logo_path=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    # Add logos if available
    add_logos(s, synk_logo_path, client_logo_path, prs.slide_width, prs.slide_height)
    # header - fit within 10" slide width with margins
    hdr = s.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9.0), Inches(0.6))
    hp = hdr.text_frame.paragraphs[0]
    hp.text = slide["title"]
    hp.font.name = "Arial"; hp.font.size = Pt(28); hp.font.bold = True
    hp.font.color.rgb = hex_to_rgb(meta["style"]["colors"]["text"])
    # table - fit within 10" slide width with margins
    table = s.shapes.add_table(len(rows)+1, len(headers), Inches(0.5), Inches(1.3), Inches(9.0), Inches(3.8)).table
    accent = hex_to_rgb(meta["style"]["colors"]["accent1"])
    for j,h in enumerate(headers):
        cell = table.cell(0,j)
        cell.text = h
        cell.fill.solid(); cell.fill.fore_color.rgb = accent
        cell.text_frame.paragraphs[0].font.name = "Arial"
        cell.text_frame.paragraphs[0].font.bold = True
    for i,r in enumerate(rows, start=1):
        for j,val in enumerate(r):
            cell = table.cell(i,j)
            cell.text = val
            cell.text_frame.paragraphs[0].font.name = "Arial"
    return s

def build_pptx(deck: dict) -> bytes:
    # MVP: wir bauen eine frische Präsentation (ohne Master), aber mit Markenfarben/Typo.
    prs = Presentation()
    # Set slide size to 16:9 (10 inches wide x 5.625 inches high)
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    meta = deck["meta"]

    # Get SYNK logo path from meta, check common filenames
    synk_logo_path = meta.get("style", {}).get("logo")
    if synk_logo_path and not os.path.exists(synk_logo_path):
        # Try without extension or with different extensions
        for ext in ['.png', '.PNG', '.jpg', '.JPG', '.jpeg', '.JPEG']:
            base_name = os.path.splitext(synk_logo_path)[0]
            test_path = base_name + ext
            if os.path.exists(test_path):
                synk_logo_path = test_path
                break

    # Get client logo path from meta
    client_logo_path = meta.get("style", {}).get("clientLogo")
    if client_logo_path and not os.path.exists(client_logo_path):
        # Try without extension or with different extensions
        for ext in ['.png', '.PNG', '.jpg', '.JPG', '.jpeg', '.JPEG']:
            base_name = os.path.splitext(client_logo_path)[0]
            test_path = base_name + ext
            if os.path.exists(test_path):
                client_logo_path = test_path
                break

    # Slides iterieren
    for sl in deck["slides"]:
        t = sl["type"]
        if t == "title":
            # No logos on title slide
            add_title_slide(prs, meta, sl)
        elif t in ["agenda","context","need","understanding","vision","approach","principles",
                   "architecture","transfer","digital","coaching","target_group","impact",
                   "about_synk","references","expertise","partners","next_steps","contact"]:
            add_text_slide(prs, meta, sl, synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)
        elif t == "modules_overview":
            headers = ["Modul","Dauer","Fokus"]
            rows = []
            for m in (sl.get("modules") or []):
                rows.append([m.get("title",""), m.get("duration",""), ""])
            add_table_slide(prs, meta, sl, headers, rows or [["—","—","—"]], synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)
        elif t == "module_detail":
            add_text_slide(prs, meta, sl, header="Modul", synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)
        elif t == "team":
            # vereinfachter Team-Text
            names = []
            for tr in (sl.get("trainers") or []):
                names.append(f"{tr.get('name','')} – {tr.get('role','')}")
            sl2 = dict(sl); sl2["content"] = names or ["tbd"]
            add_text_slide(prs, meta, sl2, header="Team", synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)
        elif t == "investment":
            # simple Pricing-Tabelle
            headers = ["Option","Leistung/Notiz","Preis"]
            rows = []
            content = sl.get("content") or []
            for c in content:
                if "–" in c:
                    left,right = c.split("–",1)
                    rows.append([left.strip(), "", right.strip()])
                else:
                    rows.append([c, "", ""])
            add_table_slide(prs, meta, sl, headers, rows or [["—","","—"]], synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)
        else:
            add_text_slide(prs, meta, sl, synk_logo_path=synk_logo_path, client_logo_path=client_logo_path)

    bio = io.BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio.read()

def build_base64(deck: dict, filename: str) -> dict:
    data = build_pptx(deck)
    return {
        "filename": filename,
        "file": base64.b64encode(data).decode("utf-8")
    }
