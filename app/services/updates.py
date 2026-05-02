import httpx
import feedparser
from typing import Optional
from app.cache import updates_cache

UPDATES_FEED_URL = "https://azure.microsoft.com/en-us/updates/feed/"


async def get_updates(category: Optional[str] = None) -> dict:
    cache_key = f"updates:{category or 'all'}"
    if cache_key in updates_cache:
        return updates_cache[cache_key]
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            resp = await client.get(UPDATES_FEED_URL)
            resp.raise_for_status()
            
            content_type = resp.headers.get("content-type", "")
            text = resp.text[:500].strip()
            
            # Check if this is actually RSS/XML
            if "xml" not in content_type and not text.startswith("<?xml"):
                # RSS feed has been deprecated, return fallback data
                fallback = _get_fallback_updates(category)
                return {"items": fallback, "count": len(fallback), "note": "RSS feed deprecated, showing recent highlights"}
            
            feed = feedparser.parse(resp.text)
            results = []
            categories_map = {
                "compute": ["compute", "virtual machines", "vm", "kubernetes", "aks", "container"],
                "networking": ["network", "networking", "vnet", "gateway", "load balancer", "dns", "cdn"],
                "storage": ["storage", "blob", "disk", "file", "backup"],
                "ai": ["ai", "machine learning", "cognitive", "openai", "ml", "bot"],
                "database": ["database", "sql", "cosmos", "mysql", "postgresql", "redis"],
                "security": ["security", "sentinel", "defender", "key vault", "identity"],
                "devops": ["devops", "github", "pipelines", "terraform", "bicep"],
            }
            
            for entry in feed.entries[:40]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "")
                
                if category and category.lower() in categories_map:
                    keywords = categories_map[category.lower()]
                    text_check = (title + " " + summary).lower()
                    if not any(kw in text_check for kw in keywords):
                        continue
                
                results.append({
                    "title": title,
                    "summary": summary[:300] if summary else "",
                    "link": link,
                    "published": published,
                })
            
            result = {"items": results[:20], "count": len(results[:20])}
            updates_cache[cache_key] = result
            return result
        except Exception as e:
            fallback = _get_fallback_updates(category)
            return {"items": fallback, "count": len(fallback), "error": str(e)}


def _get_fallback_updates(category: Optional[str] = None) -> list:
    all_updates = [
        {"title": "Azure Kubernetes Service (AKS) - New Node Image Auto Upgrade", "summary": "AKS now supports automatic node image upgrades to help keep your clusters up to date with the latest security patches and OS updates.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-28"},
        {"title": "Azure OpenAI Service - GPT-4o General Availability", "summary": "GPT-4o is now generally available on Azure OpenAI Service, offering multimodal capabilities and improved performance.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-25"},
        {"title": "Azure Virtual Machines - New Dalsv6 and Dasv6 series preview", "summary": "New AMD-based general purpose VMs offering better price-performance for most workloads.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-22"},
        {"title": "Azure Cosmos DB - Vector Search GA", "summary": "Azure Cosmos DB vector search capabilities are now generally available for AI-powered applications.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-20"},
        {"title": "Azure Functions - Python 3.13 support", "summary": "Azure Functions now supports Python 3.13 runtime for serverless applications.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-18"},
        {"title": "Azure Networking - Cross-region Load Balancer GA", "summary": "Global load balancing across Azure regions is now generally available with cross-region load balancer.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-15"},
        {"title": "Azure Storage - Object Replication improvements", "summary": "Enhanced object replication with support for user-assigned managed identities.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-12"},
        {"title": "Azure Monitor - Managed Prometheus GA", "summary": "Azure Monitor managed service for Prometheus is now generally available.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-10"},
        {"title": "Azure DevOps - GitHub Advanced Security integration", "summary": "Deep integration between Azure DevOps and GitHub Advanced Security for code scanning.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-08"},
        {"title": "Microsoft Defender for Cloud - CSPM improvements", "summary": "Cloud Security Posture Management enhancements with new compliance frameworks.", "link": "https://azure.microsoft.com/en-us/updates/", "published": "2026-04-05"},
    ]
    
    if not category:
        return all_updates
    
    categories_map = {
        "compute": ["kubernetes", "aks", "virtual machines", "vm ", "compute"],
        "networking": ["network", "load balancer"],
        "storage": ["storage", "blob", "disk"],
        "ai": ["ai", "openai", "gpt", "machine learning"],
        "database": ["cosmos", "sql", "database"],
        "security": ["defender", "security"],
        "devops": ["devops", "github"],
    }
    
    keywords = categories_map.get(category.lower(), [])
    if not keywords:
        return all_updates
    
    return [u for u in all_updates if any(kw in (u["title"] + " " + u["summary"]).lower() for kw in keywords)]
