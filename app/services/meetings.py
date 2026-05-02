import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MEETINGS_FILE = DATA_DIR / "meetings.json"


def _load_meetings(user_id: str = "") -> list:
    if MEETINGS_FILE.exists():
        try:
            all_mtg = json.loads(MEETINGS_FILE.read_text())
            if user_id:
                return [m for m in all_mtg if m.get("user_id") == user_id]
            return all_mtg
        except (json.JSONDecodeError, Exception):
            return []
    return []


def _save_meetings(meetings: list, user_id: str = ""):
    DATA_DIR.mkdir(exist_ok=True)
    all_mtg = []
    if MEETINGS_FILE.exists():
        try:
            all_mtg = json.loads(MEETINGS_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            all_mtg = []
    if user_id:
        all_mtg = [m for m in all_mtg if m.get("user_id") != user_id]
        all_mtg.extend(meetings)
    MEETINGS_FILE.write_text(json.dumps(all_mtg, indent=2, ensure_ascii=False))


async def get_meetings(user_id: str) -> dict:
    meetings = _load_meetings(user_id)
    return {"items": meetings, "count": len(meetings)}


async def create_meeting(meeting: dict, user_id: str) -> dict:
    meetings = _load_meetings(user_id)
    new_meeting = {
        "id": f"mtg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "title": meeting.get("title", ""),
        "date": meeting.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "attendees": meeting.get("attendees", ""),
        "notes": meeting.get("notes", ""),
        "actions": meeting.get("actions", []),
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    meetings.append(new_meeting)
    _save_meetings(meetings, user_id)
    return new_meeting


async def export_meeting_markdown(meeting_id: str, user_id: str) -> dict:
    meetings = _load_meetings(user_id)
    for m in meetings:
        if m.get("id") == meeting_id:
            actions = m.get("actions", [])
            md = f"""# Meeting: {m.get('title', 'Untitled')}

**Date:** {m.get('date', '')}
**Attendees:** {m.get('attendees', 'None')}

## Notes
{m.get('notes', 'No notes recorded.')}

## Action Items
{chr(10).join('- ' + a for a in actions) if actions else '- None'}
"""
            return {"markdown": md, "id": meeting_id}
    return {"markdown": "", "error": "Meeting not found"}
