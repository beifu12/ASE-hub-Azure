"""Caching layer for ASE Hub."""
from cachetools import TTLCache
from functools import wraps

# Pricing cache: max 200 entries, 10 min TTL
pricing_cache = TTLCache(maxsize=200, ttl=600)

# Updates cache: 1 hour TTL
updates_cache = TTLCache(maxsize=10, ttl=3600)

# Health cache: 5 min TTL
health_cache = TTLCache(maxsize=10, ttl=300)


def async_cached(cache, key_fn=None):
    """Decorator for async functions with TTLCache."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs) if key_fn else f"{args}:{kwargs}"
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator
