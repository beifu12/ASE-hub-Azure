"""
Authentication & Authorization module for ASE Hub.
- JWT token creation/validation
- Password hashing with bcrypt
- FastAPI dependency: get_current_user
"""
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# ── Config ─────────────────────────────────────────────────────────────
SECRET_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SECRET_FILE = SECRET_DIR / ".jwt_secret"
USERS_FILE = SECRET_DIR / "users.json"

SECRET_DIR.mkdir(exist_ok=True)

# Generate or load JWT secret
if SECRET_FILE.exists():
    SECRET_KEY = SECRET_FILE.read_text().strip()
else:
    SECRET_KEY = uuid.uuid4().hex + uuid.uuid4().hex
    SECRET_FILE.write_text(SECRET_KEY)
    SECRET_FILE.chmod(0o600)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# ── HTTP Bearer scheme ─────────────────────────────────────────────────
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _load_users() -> dict:
    """Returns {user_id: user_dict}"""
    if USERS_FILE.exists():
        try:
            items = json.loads(USERS_FILE.read_text())
            return {u["id"]: u for u in items}
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def _save_users(users: dict):
    USERS_FILE.write_text(json.dumps(list(users.values()), indent=2, ensure_ascii=False))


def get_user_by_username(username: str) -> Optional[dict]:
    users = _load_users()
    for u in users.values():
        if u["username"] == username:
            return u
    return None


def create_user(username: str, password: str, display_name: str = "") -> dict:
    users = _load_users()
    if any(u["username"] == username for u in users.values()):
        raise ValueError("Username already exists")
    user = {
        "id": uuid.uuid4().hex[:12],
        "username": username,
        "display_name": display_name or username,
        "password_hash": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    users[user["id"]] = user
    _save_users(users)
    return {k: v for k, v in user.items() if k != "password_hash"}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {k: v for k, v in user.items() if k != "password_hash"}


def create_access_token(user_id: str, username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency: extracts user from Bearer token.
    Returns {"user_id": str, "username": str}.
    Raises 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": payload["sub"], "username": payload["username"]}


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[dict]:
    """Like get_current_user but returns None instead of 401 for public endpoints."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    return {"user_id": payload["sub"], "username": payload["username"]}
