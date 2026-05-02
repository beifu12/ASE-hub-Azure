"""SQLAlchemy ORM models for ASE Hub."""
from sqlalchemy import Column, String, Text, DateTime, JSON
from datetime import datetime, timezone
from app.database import Base
import uuid


def _uid(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: _uid("usr_"))
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=lambda: _uid("rpt_"))
    user_id = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False)
    project = Column(String, default="")
    tasks = Column(JSON, default=list)
    blockers = Column(Text, default="")
    next_steps = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(String, primary_key=True, default=lambda: _uid("mtg_"))
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, default="")
    date = Column(String, nullable=False)
    attendees = Column(JSON, default=list)
    notes = Column(Text, default="")
    action_items = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(String, primary_key=True, default=lambda: _uid("bm_"))
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, default="")
    url = Column(String, default="")
    description = Column(Text, default="")


class Snippet(Base):
    __tablename__ = "snippets"
    id = Column(String, primary_key=True)
    category = Column(String, default="")
    title = Column(String, default="")
    command = Column(Text, default="")
    description = Column(Text, default="")
    user_id = Column(String, default="shared", index=True)
