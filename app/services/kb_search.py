"""Azure KB Search Service — full-text search across 1700+ KB articles."""

import json
import re
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KB_PATH = DATA_DIR / "azure_kb.json"

_kb_data = None
_kb_index = None


def _load_kb():
    global _kb_data
    if _kb_data is not None:
        return _kb_data
    if not KB_PATH.exists():
        _kb_data = []
        return _kb_data
    with open(KB_PATH, "r", encoding="utf-8") as f:
        _kb_data = json.load(f)
    return _kb_data


def _build_index():
    global _kb_index
    if _kb_index is not None:
        return _kb_index
    data = _load_kb()
    _kb_index = []
    for entry in data:
        text = (entry.get("title", "") + " " +
                entry.get("summary", "") + " " +
                entry.get("searchText", "")).lower()
        _kb_index.append({
            "id": entry.get("id", ""),
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "domain": entry.get("domain", ""),
            "service": entry.get("service", ""),
            "section": entry.get("section", ""),
            "modified": entry.get("modified", ""),
            "jd": entry.get("jd", ""),
            "text": text
        })
    return _kb_index


def search_kb(query: str, domain: str = "", service: str = "",
              page: int = 1, page_size: int = 20, max_results: int = 50):
    """Full-text search across KB articles with filtering and pagination."""
    if not query or not query.strip():
        return {"results": [], "total": 0, "page": page}

    index = _build_index()
    terms = query.lower().strip().split()
    scored = []

    for entry in index:
        # Filter by domain
        if domain and entry["domain"].lower() != domain.lower():
            continue

        # Filter by service
        if service and entry["service"].lower() != service.lower():
            continue

        text = entry["text"]
        # Calculate relevance score
        score = 0
        for term in terms:
            count = text.count(term)
            if count > 0:
                # Title matches score higher
                title_count = entry["title"].lower().count(term)
                score += count * 1 + title_count * 3

        if score > 0:
            # Add bonus for recent entries
            scored.append((score, entry))

    # Sort by relevance (descending)
    scored.sort(key=lambda x: -x[0])

    # Take top results
    total = len(scored)
    top_results = scored[:max_results]

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_results = top_results[start:end]

    # Highlight matching terms in summary
    results = []
    for _, entry in page_results:
        summary = entry["summary"]
        for term in terms:
            summary = _highlight_term(summary, term)
        results.append({
            "id": entry["id"],
            "title": entry["title"],
            "summary": summary,
            "domain": entry["domain"],
            "service": entry["service"],
            "section": entry["section"],
            "modified": entry["modified"],
            "relevance": _,
        })

    return {
        "results": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size)
    }


def _highlight_term(text: str, term: str) -> str:
    """Highlight matching term with <em> tags."""
    if not text or not term:
        return text
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return pattern.sub(lambda m: f"<em>{m.group()}</em>", text)


def get_services():
    """Get list of available domains and services for filtering."""
    data = _load_kb()
    domains = sorted(set(d.get("domain", "") for d in data if d.get("domain")))
    services = sorted(set(d.get("service", "") for d in data if d.get("service")))
    return {"domains": domains, "services": services}


def get_statistics():
    """Get KB statistics."""
    data = _load_kb()
    services = {}
    for d in data:
        svc = d.get("service", "Unknown")
        services[svc] = services.get(svc, 0) + 1
    top_services = sorted(services.items(), key=lambda x: -x[1])[:10]
    return {
        "total_entries": len(data),
        "domains": len(set(d.get("domain", "") for d in data)),
        "services": len(services),
        "top_services": [{"name": s, "count": c} for s, c in top_services]
    }
