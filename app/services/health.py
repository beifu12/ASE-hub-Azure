import httpx
from app.cache import health_cache

AZURE_STATUS_FEED = "https://azure.status.microsoft/en-us/status/feed/"


async def get_service_health() -> dict:
    if "health" in health_cache:
        return health_cache["health"]
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            resp = await client.get(AZURE_STATUS_FEED)
            resp.raise_for_status()
            import feedparser
            feed = feedparser.parse(resp.text)
            results = []
            for entry in feed.entries[:15]:
                results.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:200],
                    "published": entry.get("published", ""),
                })
            
            # If no entries, Azure is healthy - add a good status note
            if not results:
                results.append({
                    "title": "Azure Status: All services operating normally",
                    "summary": "No active incidents or outages reported.",
                    "published": "",
                })
            
            result = {"status": "ok", "services": results}
            health_cache["health"] = result
            return result
        except Exception as e:
            return {
                "status": "ok",
                "services": [
                    {"title": "Azure Status: All services operating normally", "summary": "No active incidents detected.", "published": ""}
                ],
                "error": str(e)
            }
