import httpx
from typing import Optional

MS_LEARN_URL = "https://learn.microsoft.com/api/search"


async def search_docs(q: str = "", locale: str = "en-us") -> dict:
    if not q:
        return {"items": [], "count": 0}
    
    params = {
        "search": q,
        "locale": locale,
        "scoping": "Documentation",
        "$top": 20,
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(MS_LEARN_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data.get("results", [])[:20]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                })
            return {"items": results, "count": len(results)}
        except Exception as e:
            # Fallback: generate static docs links
            fallback = [
                {
                    "title": f"Azure {q.title()} Documentation",
                    "url": f"https://learn.microsoft.com/en-us/azure/?product=popular",
                    "description": f"Search Azure documentation for '{q}' on Microsoft Learn.",
                }
            ]
            return {"items": fallback, "count": len(fallback), "error": str(e)}
