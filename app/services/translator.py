"""Azure Glossary translation service — 148 terms covering AZ-900, AZ-104, cloud native."""

import json
import re
from pathlib import Path

_GLOSSARY_PATH = Path(__file__).parent.parent / "data" / "azure_glossary.json"
_glossary: dict = {}

def _load():
    global _glossary
    if not _glossary:
        _glossary = json.loads(_GLOSSARY_PATH.read_text(encoding="utf-8"))

def translate(query: str) -> dict:
    """Search glossary for an English term, return translation info."""
    _load()
    q = query.strip().lower()

    # Exact match (case-insensitive)
    if q in _glossary:
        return {"query": query, "found": True, **_glossary[q], "match_type": "exact"}

    # Partial match — word boundaries
    matches = []
    for term, info in _glossary.items():
        # Check if query is a substring of term (with word boundary)
        if re.search(r'\b' + re.escape(q) + r'\b', term):
            matches.append({"term": term, **info})
        # Also check if term is a substring of query
        elif term in q or q in term:
            matches.append({"term": term, **info})

    if matches:
        # Prefer exact substring
        exact_sub = [m for m in matches if m["term"] == q]
        if exact_sub:
            m = exact_sub[0]
            return {"query": query, "found": True, "cn": m["cn"], "scene": m["scene"], "phonetic": m["phonetic"], "match_type": "fuzzy"}

        return {
            "query": query, "found": False,
            "suggestions": matches[:5],
            "hint": f"Found {len(matches)} partial matches — see suggestions"
        }

    # No match — search individual words
    words = q.split()
    word_matches = []
    for w in words:
        for term, info in _glossary.items():
            if w in term.split():
                word_matches.append({"term": term, "word": w, **info})

    if word_matches:
        return {
            "query": query, "found": False,
            "suggestions": word_matches[:5],
            "hint": "Broken down by word — see suggestions"
        }

    return {"query": query, "found": False, "hint": "No matches in Azure glossary"}


def search_glossary(keyword: str = "", category: str = "", limit: int = 50) -> dict:
    """Browse/search the full glossary with optional filtering."""
    _load()
    kw = keyword.strip().lower()

    results = []
    for term, info in _glossary.items():
        if category and category.lower() not in info.get("scene", "").lower():
            continue
        if kw and kw not in term and kw not in info.get("cn", ""):
            continue
        results.append({"term": term, **info})

    results.sort(key=lambda r: r["term"])
    return {"items": results[:limit], "count": len(results), "total": len(_glossary)}


def get_categories() -> list[str]:
    """Extract distinct categories/scenes from glossary."""
    _load()
    scenes = set()
    for info in _glossary.values():
        scene = info.get("scene", "")
        # Extract first part before →
        parts = re.split(r'\s*[→>]\s*', scene)
        scenes.add(parts[0].strip())
    return sorted(scenes)
