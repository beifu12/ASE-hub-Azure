import httpx
from typing import Optional

AZURE_PRICES_URL = "https://prices.azure.com/api/retail/prices"


async def search_pricing(keyword: str = "", region: Optional[str] = None) -> dict:
    escaped_keyword = keyword.replace("'", "''") if keyword else ""
    escaped_region = region.replace("'", "''") if region else ""
    
    filters = []
    if escaped_keyword:
        upper_keyword = escaped_keyword.upper()
        filters.append(
            f"(contains(toupper(serviceName), '{upper_keyword}') "
            f"or contains(toupper(productName), '{upper_keyword}') "
            f"or contains(toupper(meterName), '{upper_keyword}'))"
        )
    if escaped_region:
        filters.append(f"contains(toupper(armRegionName), '{escaped_region.upper()}')")
    
    filter_str = " and ".join(filters) if filters else None
    
    params = {"api-version": "2023-01-01-preview"}
    if filter_str:
        params["$filter"] = filter_str
        params["$top"] = "200"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(AZURE_PRICES_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("Items", [])
            results = []
            for item in items[:50]:
                results.append({
                    "serviceName": item.get("serviceName", ""),
                    "armRegionName": item.get("armRegionName", ""),
                    "unitPrice": item.get("unitPrice", 0),
                    "meterName": item.get("meterName", ""),
                    "productName": item.get("productName", ""),
                    "currencyCode": item.get("currencyCode", "USD"),
                })
            return {"items": results, "count": len(results), "total": data.get("Count", 0)}
        except Exception as e:
            return {"items": [], "count": 0, "total": 0, "error": str(e)}
