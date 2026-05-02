"""One-off migration script: JSON files → SQLite.

Usage:  python scripts/migrate_json_to_sqlite.py
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "ase_hub.db"

# Ensure data dir exists
DATA_DIR.mkdir(exist_ok=True)


def migrate_users(conn):
    users_file = DATA_DIR / "users.json"
    if not users_file.exists():
        print("  [SKIP] users.json not found")
        return

    users = json.loads(users_file.read_text())
    if not users:
        print("  [SKIP] users.json is empty")
        return

    rows = []
    for u in users:
        rows.append((
            u.get("id", ""),
            u.get("username", ""),
            u.get("display_name", u.get("username", "")),
            u.get("password_hash", ""),
            u.get("created_at", ""),
        ))

    conn.executemany(
        "INSERT OR IGNORE INTO users (id, username, display_name, password_hash, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"  [OK] Migrated {len(rows)} users")


def migrate_reports(conn):
    reports_file = DATA_DIR / "reports.json"
    if not reports_file.exists():
        print("  [SKIP] reports.json not found")
        return

    reports = json.loads(reports_file.read_text())
    if not reports:
        print("  [SKIP] reports.json is empty")
        return

    rows = []
    for r in reports:
        rows.append((
            r.get("id", ""),
            r.get("user_id", ""),
            r.get("date", ""),
            r.get("project", ""),
            json.dumps(r.get("tasks", [])),
            r.get("blockers", "") or "",
            r.get("next_steps", "") or "",
            r.get("created_at", ""),
        ))

    conn.executemany(
        "INSERT OR IGNORE INTO reports (id, user_id, date, project, tasks, blockers, next_steps, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"  [OK] Migrated {len(rows)} reports")


def migrate_meetings(conn):
    meetings_file = DATA_DIR / "meetings.json"
    if not meetings_file.exists():
        print("  [SKIP] meetings.json not found")
        return

    meetings = json.loads(meetings_file.read_text())
    if not meetings:
        print("  [SKIP] meetings.json is empty")
        return

    rows = []
    for m in meetings:
        # Old JSON uses "actions", new model uses "action_items"
        action_items = m.get("action_items") or m.get("actions") or []
        rows.append((
            m.get("id", ""),
            m.get("user_id", ""),
            m.get("title", ""),
            m.get("date", ""),
            json.dumps(m.get("attendees", []) if isinstance(m.get("attendees"), list) else [m.get("attendees", "")]),
            m.get("notes", "") or "",
            json.dumps(action_items),
            m.get("created_at", ""),
        ))

    conn.executemany(
        "INSERT OR IGNORE INTO meetings (id, user_id, title, date, attendees, notes, action_items, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"  [OK] Migrated {len(rows)} meetings")


def migrate_bookmarks(conn):
    bookmarks_file = DATA_DIR / "bookmarks.json"
    if not bookmarks_file.exists():
        print("  [SKIP] bookmarks.json not found")
        return

    bookmarks = json.loads(bookmarks_file.read_text())
    if not bookmarks:
        print("  [SKIP] bookmarks.json is empty")
        return

    rows = []
    for b in bookmarks:
        rows.append((
            b.get("id", ""),
            b.get("user_id", ""),
            b.get("title", ""),
            b.get("url", ""),
            b.get("description", "") or "",
        ))

    conn.executemany(
        "INSERT OR IGNORE INTO bookmarks (id, user_id, title, url, description) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"  [OK] Migrated {len(rows)} bookmarks")


def main():
    print("ASE Hub JSON → SQLite Migration")
    print(f"  Database: {DB_PATH}")
    print()

    # Ensure tables exist (run init_db equivalent)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT DEFAULT '',
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            project TEXT DEFAULT '',
            tasks TEXT DEFAULT '[]',
            blockers TEXT DEFAULT '',
            next_steps TEXT DEFAULT '',
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT DEFAULT '',
            date TEXT NOT NULL,
            attendees TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            action_items TEXT DEFAULT '[]',
            created_at TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT DEFAULT '',
            url TEXT DEFAULT '',
            description TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS snippets (
            id TEXT PRIMARY KEY,
            category TEXT DEFAULT '',
            title TEXT DEFAULT '',
            command TEXT DEFAULT '',
            description TEXT DEFAULT '',
            user_id TEXT DEFAULT 'shared'
        );
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
        CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id);
        CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
        CREATE INDEX IF NOT EXISTS idx_snippets_user_id ON snippets(user_id);
    """)
    conn.commit()

    migrate_users(conn)
    migrate_reports(conn)
    migrate_meetings(conn)
    migrate_bookmarks(conn)

    # Verify
    for table in ["users", "reports", "meetings", "bookmarks"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  [{table}: {count} rows]")

    conn.close()
    print()
    print("Migration complete.")


if __name__ == "__main__":
    main()
