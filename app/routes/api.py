import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from app.services import pricing, docs, updates, health, reports, meetings, snippets
from app.auth import (
    get_current_user, get_optional_user,
    get_user_by_username, create_user, authenticate_user, create_access_token,
)

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
BOOKMARKS_FILE = DATA_DIR / "bookmarks.json"


def _load_bookmarks(user_id: str = "") -> list:
    if BOOKMARKS_FILE.exists():
        try:
            all_bm = json.loads(BOOKMARKS_FILE.read_text())
            if user_id:
                return [b for b in all_bm if b.get("user_id") == user_id]
            return all_bm
        except (json.JSONDecodeError, Exception):
            return []
    return []


def _save_bookmarks(bookmarks: list, user_id: str = ""):
    DATA_DIR.mkdir(exist_ok=True)
    # Merge: keep bookmarks from other users, replace current user's
    all_bm = []
    if BOOKMARKS_FILE.exists():
        try:
            all_bm = json.loads(BOOKMARKS_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            all_bm = []
    if user_id:
        all_bm = [b for b in all_bm if b.get("user_id") != user_id]
        all_bm.extend(bookmarks)
    BOOKMARKS_FILE.write_text(json.dumps(all_bm, indent=2, ensure_ascii=False))


# ═══════════ AUTH ═══════════

@router.post("/auth/register")
async def api_register(request: Request):
    body = await request.json()
    username = body.get("username", "").strip()
    password = body.get("password", "")
    display_name = body.get("display_name", username)

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    if len(username) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    try:
        user = create_user(username, password, display_name)
        token = create_access_token(user["id"], user["username"])
        return {"user": user, "access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/auth/login")
async def api_login(request: Request):
    body = await request.json()
    username = body.get("username", "").strip()
    password = body.get("password", "")

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user["id"], user["username"])
    return {"user": user, "access_token": token, "token_type": "bearer"}


@router.get("/auth/me")
async def api_me(user: dict = Depends(get_current_user)):
    full_user = get_user_by_username(user["username"])
    if full_user:
        return {k: v for k, v in full_user.items() if k != "password_hash"}
    return user


# ═══════════ PUBLIC (no auth) ═══════════

@router.get("/health")
async def api_health():
    return {"status": "healthy", "service": "ASE Hub", "version": "1.0.0"}


@router.get("/pricing")
async def api_pricing(keyword: str = "", region: Optional[str] = None):
    return await pricing.search_pricing(keyword=keyword, region=region)


@router.get("/docs")
async def api_docs(q: str = ""):
    return await docs.search_docs(q=q)


@router.get("/updates")
async def api_updates(category: Optional[str] = None):
    return await updates.get_updates(category=category)


@router.get("/status")
async def api_status():
    return await health.get_service_health()


# ═══════════ PROTECTED (require auth) ═══════════

@router.get("/reports")
async def api_get_reports(user: dict = Depends(get_current_user)):
    return await reports.get_reports(user["user_id"])


@router.post("/reports")
async def api_create_report(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    return await reports.create_report(body, user["user_id"])


@router.get("/reports/{report_id}/markdown")
async def api_report_markdown(report_id: str, user: dict = Depends(get_current_user)):
    return await reports.export_report_markdown(report_id, user["user_id"])


@router.get("/meetings")
async def api_get_meetings(user: dict = Depends(get_current_user)):
    return await meetings.get_meetings(user["user_id"])


@router.post("/meetings")
async def api_create_meeting(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    return await meetings.create_meeting(body, user["user_id"])


@router.get("/meetings/{meeting_id}/markdown")
async def api_meeting_markdown(meeting_id: str, user: dict = Depends(get_current_user)):
    return await meetings.export_meeting_markdown(meeting_id, user["user_id"])


@router.get("/snippets")
async def api_snippets(category: Optional[str] = None, user: dict = Depends(get_current_user)):
    return await snippets.get_snippets(category=category or "", user_id=user["user_id"])


@router.get("/bookmarks")
async def api_get_bookmarks(user: dict | None = Depends(get_optional_user)):
    bookmarks = _load_bookmarks(user["user_id"] if user else "")
    return {"items": bookmarks, "count": len(bookmarks)}


@router.post("/bookmarks")
async def api_create_bookmark(request: Request, user: dict = Depends(get_current_user)):
    bookmarks = _load_bookmarks(user["user_id"])
    body = await request.json()
    new_bm = {
        "id": f"bm_{len(bookmarks) + 1}_{user['user_id'][:6]}",
        "title": body.get("title", ""),
        "url": body.get("url", ""),
        "description": body.get("description", ""),
        "user_id": user["user_id"],
    }
    bookmarks.append(new_bm)
    _save_bookmarks(bookmarks, user["user_id"])
    return new_bm
