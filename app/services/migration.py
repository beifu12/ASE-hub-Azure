"""Migration knowledge base service for ASE Hub."""
import json
from pathlib import Path
from typing import Optional

KB_PATH = Path(__file__).resolve().parent.parent / "data" / "migration_kb.json"

_kb_cache: list | None = None


def _load_kb() -> list:
    global _kb_cache
    if _kb_cache is None:
        if KB_PATH.exists():
            _kb_cache = json.loads(KB_PATH.read_text())
        else:
            _kb_cache = []
    return _kb_cache


async def get_all_services() -> list:
    return _load_kb()


async def check_service(service_name: str) -> Optional[dict]:
    """Exact match on service name (case-insensitive)."""
    name = service_name.lower()
    for svc in _load_kb():
        if svc["serviceName"].lower() == name:
            return svc
    return None


async def search_services(keyword: str) -> list:
    """Search by keyword in serviceName or categories."""
    kw = keyword.lower()
    results = []
    for svc in _load_kb():
        if kw in svc["serviceName"].lower() or any(
            kw in cat.lower() for cat in svc.get("categories", [])
        ):
            results.append(svc)
    return results


async def get_unsupported_services() -> list:
    """Return services that do NOT support cross-subscription moves."""
    return [s for s in _load_kb() if not s.get("crossSubscriptionMove", True)]
