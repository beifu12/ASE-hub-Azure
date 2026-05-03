"""Rate limiting middleware for ASE Hub."""
import time
from collections import defaultdict

from fastapi import Request, HTTPException

# In-memory rate limit store: {client_ip: [(timestamp, path), ...]}
_attempts = defaultdict(list)

LOGIN_LIMIT = 5   # max attempts per minute
LOGIN_WINDOW = 60  # seconds


def clean_old(ip: str):
    """Remove entries older than the window."""
    now = time.time()
    _attempts[ip] = [e for e in _attempts[ip] if now - e[0] < LOGIN_WINDOW]


async def rate_limit_middleware(request: Request, call_next):
    # Only rate-limit login endpoint
    if request.url.path == "/api/auth/login" and request.method == "POST":
        ip = request.client.host if request.client else "unknown"
        clean_old(ip)

        if len(_attempts[ip]) >= LOGIN_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please wait 1 minute and try again.",
            )

        _attempts[ip].append((time.time(), request.url.path))

    return await call_next(request)


# ═══════════ LOGIN GATE ═══════════

from fastapi.responses import RedirectResponse, JSONResponse as GateJSON

async def login_gate_middleware(request: Request, call_next):
    """Require authentication for all non-public paths."""
    PUBLIC = ["/login", "/api/auth/login", "/api/auth/status", "/api/health", "/api/kb/", "/static/"]
    path = request.url.path
    if any(path.startswith(p) for p in PUBLIC):
        return await call_next(request)

    # Check cookie first, then Authorization header
    token = request.cookies.get("ase_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]

    if not token:
        if path.startswith("/api/"):
            return GateJSON({"detail": "Authentication required"}, status_code=401)
        return RedirectResponse(url="/login", status_code=302)

    from app.auth import decode_token
    payload = decode_token(token)
    if payload is None:
        if path.startswith("/api/"):
            return GateJSON({"detail": "Invalid or expired token"}, status_code=401)
        return RedirectResponse(url="/login", status_code=302)

    request.state.user = payload
    return await call_next(request)
