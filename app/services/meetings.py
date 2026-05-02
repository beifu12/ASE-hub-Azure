from sqlalchemy import select
from app.database import async_session
from app.models import Meeting


def _serialize(meeting: Meeting) -> dict:
    return {
        "id": meeting.id,
        "user_id": meeting.user_id,
        "title": meeting.title,
        "date": meeting.date,
        "attendees": meeting.attendees or [],
        "notes": meeting.notes or "",
        "action_items": meeting.action_items or [],
        "created_at": meeting.created_at.isoformat() if meeting.created_at else "",
    }


async def get_meetings(user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Meeting).where(Meeting.user_id == user_id)
        )
        meetings = result.scalars().all()
        return {"items": [_serialize(m) for m in meetings], "count": len(meetings)}


async def create_meeting(meeting: dict, user_id: str) -> dict:
    async with async_session() as db:
        mtg = Meeting(
            user_id=user_id,
            title=meeting.get("title", ""),
            date=meeting.get("date", ""),
            attendees=meeting.get("attendees", []),
            notes=meeting.get("notes", ""),
            action_items=meeting.get("action_items", []),
        )
        db.add(mtg)
        await db.commit()
        await db.refresh(mtg)
        return _serialize(mtg)


async def export_meeting_markdown(meeting_id: str, user_id: str) -> dict:
    async with async_session() as db:
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_id, Meeting.user_id == user_id)
        )
        m = result.scalars().first()
        if not m:
            return {"markdown": "", "error": "Meeting not found"}
        actions = m.action_items or []
        attendees = m.attendees
        if isinstance(attendees, list):
            attendees = ", ".join(attendees)
        md = f"""# Meeting: {m.title or 'Untitled'}

**Date:** {m.date}
**Attendees:** {attendees or 'None'}

## Notes
{m.notes or 'No notes recorded.'}

## Action Items
{chr(10).join('- ' + a for a in actions) if actions else '- None'}
"""
        return {"markdown": md, "id": meeting_id}
