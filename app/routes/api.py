from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, HTTPException
from app.services import pricing, docs, updates, health, reports, meetings, snippets, migration
from app.auth import (
    get_current_user, get_optional_user,
    get_user_by_username, create_user, authenticate_user, create_access_token,
)
from app.database import get_db
from app.models import Bookmark, User as UserModel
from app.schemas import (
    LoginRequest, AdminCreateUserRequest,
    ReportCreateRequest, ReportUpdateRequest,
    MeetingCreateRequest, MeetingUpdateRequest,
    BookmarkCreateRequest,
)

router = APIRouter()


def _serialize_bookmark(b: Bookmark) -> dict:
    return {
        "id": b.id, "title": b.title, "url": b.url,
        "description": b.description, "user_id": b.user_id,
    }


# ═══════════ AUTH STATUS ═══════════

@router.get("/auth/status")
async def api_auth_status():
    return {"registration_open": False, "instance_type": "private"}


@router.post("/auth/register")
async def api_register():
    raise HTTPException(status_code=403, detail="Registration is closed. Use admin panel.")


@router.post("/auth/login")
async def api_login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user["id"], user["username"])
    return {"user": user, "access_token": token, "token_type": "bearer"}


@router.get("/auth/me")
async def api_me(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    full_user = await get_user_by_username(db, user["username"])
    if full_user:
        return {
            "id": full_user.id, "username": full_user.username,
            "display_name": full_user.display_name,
            "created_at": full_user.created_at.isoformat(),
        }
    return user


# ═══════════ ADMIN ═══════════

@router.get("/admin/users")
async def admin_list_users(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return {
        "items": [{
            "id": u.id, "username": u.username,
            "display_name": u.display_name,
            "created_at": u.created_at.isoformat() if u.created_at else "",
        } for u in users],
        "count": len(users),
    }


@router.post("/admin/users")
async def admin_create_user(
    body: AdminCreateUserRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    username = body.username.strip()
    password = body.password
    display_name = body.display_name or username
    try:
        new_user = await create_user(db, username, password, display_name)
        return {"user": new_user}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_id == user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(target)
    await db.commit()
    return {"deleted": True, "user_id": user_id}


# ═══════════ PUBLIC ═══════════

@router.get("/health")
async def api_health(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "service": "ASE Hub",
        "version": "2.1.0"
    }


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


@router.get("/migration/services")
async def api_migration_services(unsupported_only: bool = False):
    if unsupported_only:
        services = await migration.get_unsupported_services()
        return {"items": services, "count": len(services)}
    services = await migration.get_all_services()
    return {"items": services, "count": len(services)}


@router.get("/migration/check")
async def api_migration_check(service: str = ""):
    if not service:
        return {"error": "service parameter required"}
    result = await migration.check_service(service)
    if result:
        return {"found": True, "service": result}
    return {"found": False, "service": service, "message": "Service not found in migration knowledge base"}


@router.get("/migration/search")
async def api_migration_search(keyword: str = ""):
    if not keyword:
        return {"items": [], "count": 0}
    results = await migration.search_services(keyword)
    return {"items": results, "count": len(results)}


# ═══════════ PROTECTED ═══════════

@router.get("/reports")
async def api_get_reports(user: dict = Depends(get_current_user)):
    return await reports.get_reports(user["user_id"])


@router.post("/reports")
async def api_create_report(body: ReportCreateRequest, user: dict = Depends(get_current_user)):
    return await reports.create_report(body.model_dump(), user["user_id"])


@router.put("/reports/{report_id}")
async def api_update_report(report_id: str, body: ReportUpdateRequest, user: dict = Depends(get_current_user)):
    return await reports.update_report(report_id, body.model_dump(exclude_none=True), user["user_id"])


@router.delete("/reports/{report_id}")
async def api_delete_report(report_id: str, user: dict = Depends(get_current_user)):
    return await reports.delete_report(report_id, user["user_id"])



@router.get("/reports/{report_id}/markdown")
async def api_report_markdown(report_id: str, user: dict = Depends(get_current_user)):
    return await reports.export_report_markdown(report_id, user["user_id"])


@router.get("/meetings")
async def api_get_meetings(user: dict = Depends(get_current_user)):
    return await meetings.get_meetings(user["user_id"])


@router.post("/meetings")
async def api_create_meeting(body: MeetingCreateRequest, user: dict = Depends(get_current_user)):
    return await meetings.create_meeting(body.model_dump(), user["user_id"])


@router.put("/meetings/{meeting_id}")
async def api_update_meeting(meeting_id: str, body: MeetingUpdateRequest, user: dict = Depends(get_current_user)):
    return await meetings.update_meeting(meeting_id, body.model_dump(exclude_none=True), user["user_id"])


@router.delete("/meetings/{meeting_id}")
async def api_delete_meeting(meeting_id: str, user: dict = Depends(get_current_user)):
    return await meetings.delete_meeting(meeting_id, user["user_id"])



@router.get("/meetings/{meeting_id}/markdown")
async def api_meeting_markdown(meeting_id: str, user: dict = Depends(get_current_user)):
    return await meetings.export_meeting_markdown(meeting_id, user["user_id"])


@router.get("/snippets")
async def api_snippets(category: Optional[str] = None, user: dict = Depends(get_current_user)):
    return await snippets.get_snippets(category=category or "", user_id=user["user_id"])


@router.get("/bookmarks")
async def api_get_bookmarks(
    user: dict | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Bookmark)
    if user:
        query = query.where(Bookmark.user_id == user["user_id"])
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    items = [_serialize_bookmark(b) for b in bookmarks]
    return {"items": items, "count": len(items)}


@router.post("/bookmarks")
async def api_create_bookmark(
    body: BookmarkCreateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bm = Bookmark(
        user_id=user["user_id"],
        title=body.title,
        url=body.url,
        description=body.description,
    )
    db.add(bm)
    await db.commit()
    await db.refresh(bm)
    return _serialize_bookmark(bm)
