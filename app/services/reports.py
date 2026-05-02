from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import async_session
from app.models import Report


def _serialize(report: Report) -> dict:
    return {
        "id": report.id,
        "user_id": report.user_id,
        "date": report.date,
        "project": report.project,
        "tasks": report.tasks or [],
        "blockers": report.blockers or "",
        "next_steps": report.next_steps or "",
        "created_at": report.created_at.isoformat() if report.created_at else "",
    }


async def get_reports(user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Report).where(Report.user_id == user_id)
        )
        reports = result.scalars().all()
        return {"items": [_serialize(r) for r in reports], "count": len(reports)}


async def create_report(report: dict, user_id: str) -> dict:
    async with async_session() as db:
        rpt = Report(
            user_id=user_id,
            date=report.get("date", ""),
            project=report.get("project", ""),
            tasks=report.get("tasks", []),
            blockers=report.get("blockers", ""),
            next_steps=report.get("next_steps", ""),
        )
        db.add(rpt)
        await db.commit()
        await db.refresh(rpt)
        return _serialize(rpt)


async def update_report(report_id: str, updates: dict, user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Report).where(Report.id == report_id, Report.user_id == user_id)
        )
        r = result.scalars().first()
        if not r:
            return {"error": "Report not found or not yours"}
        for field in ("date", "project", "tasks", "blockers", "next_steps"):
            if field in updates and updates[field] is not None:
                setattr(r, field, updates[field])
        await db.commit()
        await db.refresh(r)
        return _serialize(r)


async def delete_report(report_id: str, user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Report).where(Report.id == report_id, Report.user_id == user_id)
        )
        r = result.scalars().first()
        if not r:
            return {"error": "Report not found or not yours"}
        await db.delete(r)
        await db.commit()
        return {"deleted": True, "id": report_id}


async def export_report_markdown(report_id: str, user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Report).where(Report.id == report_id, Report.user_id == user_id)
        )
        r = result.scalars().first()
        if not r:
            return {"markdown": "", "error": "Report not found"}
        tasks = r.tasks or []
        md = f"""# Daily Work Report

**Date:** {r.date}
**Project:** {r.project}

## Tasks Completed
{chr(10).join('- ' + t for t in tasks) if tasks else '- None'}

## Blockers
{r.blockers or 'None'}

## Next Steps
{r.next_steps or 'None'}
"""
        return {"markdown": md, "id": report_id}
