# Robustness Layer - JSON Sanitizer

## Überblick

Der **JSON Sanitizer** ist eine Sicherheitsschicht, die automatisch fehlerhafte oder unvollständige JSON-Eingaben von LLMs (z.B. Copilot-Agenten) korrigiert und normalisiert.

## Problem

Wenn ein LLM JSON-Strukturen generiert, können folgende Fehler auftreten:

- ❌ Fehlende Pflichtfelder (`meta`, `slides`, `style`)
- ❌ Falsche Datentypen (String statt Liste)
- ❌ Ungültige Farbcodes (`"blue"` statt `"#0000FF"`)
- ❌ Unbekannte Slide-Types
- ❌ Fehlende IDs oder Titel
- ❌ Gefährliche Zeichen in Dateinamen
- ❌ Leere Slide-Arrays

## Lösung

Der Sanitizer fängt diese Fehler ab und korrigiert sie automatisch:

✅ **Pflichtfelder**: Werden mit sinnvollen Defaults befüllt
✅ **Typen**: String → Liste, Null → Empty Array
✅ **Farben**: Ungültige Hex-Codes werden durch Defaults ersetzt
✅ **Slide-Types**: Unbekannte Types → "text"
✅ **IDs/Titel**: Automatisch generiert falls fehlend
✅ **Dateinamen**: Gefährliche Zeichen entfernt (Path Traversal Protection)
✅ **Leere Decks**: Default-Titelfolie wird erstellt

## Aktivierung

Der Sanitizer ist **automatisch aktiv** in beiden API-Endpoints:

- `POST /render` → Gibt Base64-encoded PPTX zurück
- `POST /render/bytes` → Gibt rohe PPTX-Bytes zurück

Beide Endpoints verwenden intern `validate_and_sanitize()`.

## Funktionsweise

### 1. Automatische Korrektur

**Eingabe vom Copilot (fehlerhaft):**
```json
{
  "deck": {
    "meta": {
      "customer": "../../../etc/passwd",
      "style": {
        "colors": {
          "primary": "blue"
        }
      }
    },
    "slides": []
  }
}
```

**Nach Sanitization:**
```json
{
  "deck": {
    "meta": {
      "customer": "etcpasswd",
      "deckTitle": "Presentation",
      "author": "SYNK GROUP",
      "date": "2025-01-01",
      "style": {
        "font": "Arial",
        "colors": {
          "primary": "#06206F",
          "accent1": "#2FCAC3",
          "accent2": "#966668",
          "text": "#011533",
          "background": "#FFFFFF"
        }
      }
    },
    "slides": [
      {
        "id": "01",
        "type": "title",
        "title": "Presentation"
      }
    ]
  }
}
```

### 2. Logging für Debugging

Der Sanitizer loggt alle Korrekturen:

```
2025-11-13 08:14:50 - json_sanitizer - WARNING - Invalid hex color '#blue', using fallback #06206F
2025-11-13 08:14:50 - json_sanitizer - INFO - Converted content from string to list in slide 01
2025-11-13 08:14:50 - json_sanitizer - INFO - Added missing ID: slide_01
```

So können Sie nachvollziehen, welche Fehler der Copilot gemacht hat.

### 3. HTTP-Header für Transparenz

Die API fügt Header hinzu, um zu zeigen, dass Sanitization aktiv war:

```http
X-PPTX-Sanitized: true
X-PPTX-Builder-Version: v2-2025-10-16
```

## Beispiele

### Beispiel 1: Fehlende Meta-Daten

**Input:**
```json
{
  "deck": {
    "slides": [
      {"type": "title", "title": "Hello"}
    ]
  }
}
```

**Ergebnis:** ✅ Meta-Daten werden mit Defaults befüllt

---

### Beispiel 2: String statt Array

**Input:**
```json
{
  "deck": {
    "slides": [
      {
        "type": "agenda",
        "title": "Agenda",
        "content": "Single string instead of array"
      }
    ]
  }
}
```

**Ergebnis:** ✅ Content wird zu `["Single string instead of array"]`

---

### Beispiel 3: Ungültige Farben

**Input:**
```json
{
  "deck": {
    "meta": {
      "style": {
        "colors": {
          "primary": "red",
          "accent1": "#GGG"
        }
      }
    }
  }
}
```

**Ergebnis:** ✅ Farben werden durch valide Hex-Codes ersetzt

---

### Beispiel 4: Unbekannter Slide-Type

**Input:**
```json
{
  "deck": {
    "slides": [
      {"type": "custom_type_xyz", "title": "Test"}
    ]
  }
}
```

**Ergebnis:** ✅ Type wird zu `"text"` konvertiert

## Programmatische Nutzung

Falls Sie den Sanitizer direkt verwenden möchten:

```python
from json_sanitizer import validate_and_sanitize

# Raw JSON vom Copilot
raw_payload = {
    "deck": {
        # ... potentially broken JSON
    }
}

try:
    # Sanitize
    clean_deck = validate_and_sanitize(raw_payload)

    # Now safe to use
    pptx_bytes = build_pptx(clean_deck)

except ValueError as e:
    # Only raised if payload is completely invalid
    print(f"Cannot fix this: {e}")
```

## Validierungsregeln

| Feld | Regel | Default |
|------|-------|---------|
| `meta.customer` | Sanitized filename | `"Client"` |
| `meta.deckTitle` | Sanitized filename | `"Presentation"` |
| `meta.author` | String | `"SYNK GROUP"` |
| `meta.date` | String | `"2025-01-01"` |
| `style.font` | String | `"Arial"` |
| `style.colors.*` | Valid 6-char hex | Default colors |
| `slides[].id` | Non-empty string | `"slide_01"`, `"slide_02"`, ... |
| `slides[].type` | Valid slide type | `"text"` |
| `slides[].title` | Non-empty string | `"Slide N"` |
| `slides[].content` | List | `[]` or converted from string |

## Gültige Slide-Types

```
title, agenda, context, need, understanding, vision,
approach, principles, architecture, modules_overview,
module_detail, transfer, digital, coaching, target_group,
impact, about_synk, team, references, expertise, partners,
investment, next_steps, contact
```

Alle anderen Types werden zu `"text"` konvertiert.

## Tests

Führen Sie die Sanitizer-Tests aus:

```bash
python test_sanitizer.py
```

Ergebnis:
```
✓ TEST 1: Missing meta and minimal structure
✓ TEST 2: Invalid hex colors
✓ TEST 3: String content instead of list
✓ TEST 4: Invalid slide type
✓ TEST 5: Empty slides array
✓ TEST 6: Dangerous filename characters
✓ TEST 7: Missing IDs and titles
✓ TEST 8: Completely broken payload
```

## Vorteile für Copilot-Integration

1. **Fehlertoleranz**: LLM-Fehler werden automatisch korrigiert
2. **Weniger Debugging**: Keine manuellen JSON-Korrekturen nötig
3. **Sicherheit**: Path Traversal und Injection-Angriffe verhindert
4. **Transparenz**: Alle Korrekturen werden geloggt
5. **Produktivität**: Copilot kann "grob" arbeiten, Sanitizer macht es perfekt

## Grenzen

Der Sanitizer kann **nicht** korrigieren:

- ❌ Komplett fehlendes `"deck"` Objekt
- ❌ Nicht-JSON Input (z.B. Plain Text)
- ❌ Zirkuläre Referenzen

In diesen Fällen wird ein `400 Bad Request` mit Fehlermeldung zurückgegeben.

## Deaktivierung

Falls Sie den Sanitizer ausschalten möchten (nicht empfohlen):

```python
# In app.py, ersetze:
deck = _extract_and_sanitize_deck(payload)

# Durch die alte Funktion:
deck = _extract_deck(payload)
```

**Wichtig**: Ohne Sanitizer sind Sie anfällig für LLM-Fehler!

## Status

✅ **Aktiv seit Version:** v2-2025-10-16
✅ **Status:** Production Ready
✅ **Tests:** 8/8 passing
✅ **Coverage:** Meta, Slides, Colors, Types, Security

## Support

Bei Problemen:
1. Logs prüfen (detaillierte Fehler)
2. `test_sanitizer.py` ausführen
3. Issue auf GitHub öffnen

---

**Fazit:** Der Robustness Layer macht Ihr System resilient gegen LLM-Fehler und ermöglicht eine stabile Copilot-Integration! 🚀
