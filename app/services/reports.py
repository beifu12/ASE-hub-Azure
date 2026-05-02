import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
REPORTS_FILE = DATA_DIR / "reports.json"


def _load_reports(user_id: str = "") -> list:
    if REPORTS_FILE.exists():
        try:
            all_rpt = json.loads(REPORTS_FILE.read_text())
            if user_id:
                return [r for r in all_rpt if r.get("user_id") == user_id]
            return all_rpt
        except (json.JSONDecodeError, Exception):
            return []
    return []


def _save_reports(reports: list, user_id: str = ""):
    DATA_DIR.mkdir(exist_ok=True)
    all_rpt = []
    if REPORTS_FILE.exists():
        try:
            all_rpt = json.loads(REPORTS_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            all_rpt = []
    if user_id:
        all_rpt = [r for r in all_rpt if r.get("user_id") != user_id]
        all_rpt.extend(reports)
    REPORTS_FILE.write_text(json.dumps(all_rpt, indent=2, ensure_ascii=False))


async def get_reports(user_id: str) -> dict:
    reports = _load_reports(user_id)
    return {"items": reports, "count": len(reports)}


async def create_report(report: dict, user_id: str) -> dict:
    reports = _load_reports(user_id)
    new_report = {
        "id": f"rpt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "date": report.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "project": report.get("project", ""),
        "tasks": report.get("tasks", []),
        "blockers": report.get("blockers", ""),
        "next_steps": report.get("next_steps", ""),
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    reports.append(new_report)
    _save_reports(reports, user_id)
    return new_report


async def export_report_markdown(report_id: str, user_id: str) -> dict:
    reports = _load_reports(user_id)
    for r in reports:
        if r.get("id") == report_id:
            tasks = r.get("tasks", [])
            md = f"""# Daily Work Report

**Date:** {r.get('date', '')}
**Project:** {r.get('project', '')}

## Tasks Completed
{chr(10).join('- ' + t for t in tasks) if tasks else '- None'}

## Blockers
{r.get('blockers', 'None')}

## Next Steps
{r.get('next_steps', 'None')}
"""
            return {"markdown": md, "id": report_id}
    return {"markdown": "", "error": "Report not found"}
