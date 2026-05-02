"""
Authentication & Authorization module for ASE Hub.
- JWT token creation/validation
- Password hashing with bcrypt
- FastAPI dependency: get_current_user
"""
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select

from app.database import get_db
from app.models import User

# ── Config ─────────────────────────────────────────────────────────────
SECRET_DIR = Path(__file__).resolve().parent.parent / "data"
SECRET_FILE = SECRET_DIR / ".jwt_secret"

SECRET_DIR.mkdir(exist_ok=True)

if SECRET_FILE.exists():
    SECRET_KEY = SECRET_FILE.read_text().strip()
else:
    SECRET_KEY = os.environ.get("JWT_SECRET") or (uuid.uuid4().hex + uuid.uuid4().hex)
    SECRET_FILE.write_text(SECRET_KEY)
    SECRET_FILE.chmod(0o600)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


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


async def get_user_by_username(db, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db, username: str, password: str, display_name: str = "") -> dict:
    existing = await get_user_by_username(db, username)
    if existing:
        raise ValueError("Username already exists")
    user = User(
        username=username,
        display_name=display_name or username,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "created_at": user.created_at.isoformat(),
    }


async def authenticate_user(db, username: str, password: str) -> Optional[dict]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "created_at": user.created_at.isoformat(),
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
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
