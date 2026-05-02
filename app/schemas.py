"""Pydantic request/response schemas for ASE Hub."""
from pydantic import BaseModel, Field
from typing import Optional


# ═══════════ Auth ═══════════

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str = ""
    created_at: str = ""


class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


# ═══════════ Admin ═══════════

class AdminCreateUserRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)
    display_name: Optional[str] = None


# ═══════════ Reports ═══════════

class ReportCreateRequest(BaseModel):
    date: str = ""
    project: str = ""
    tasks: list[str] = Field(default_factory=list)
    blockers: str = ""
    next_steps: str = ""


class ReportUpdateRequest(BaseModel):
    date: Optional[str] = None
    project: Optional[str] = None
    tasks: Optional[list[str]] = None
    blockers: Optional[str] = None
    next_steps: Optional[str] = None


# ═══════════ Meetings ═══════════

class MeetingCreateRequest(BaseModel):
    title: str = ""
    date: str = ""
    attendees: list[str] = Field(default_factory=list)
    notes: str = ""
    action_items: list[str] = Field(default_factory=list)


class MeetingUpdateRequest(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    attendees: Optional[list[str]] = None
    notes: Optional[str] = None
    action_items: Optional[list[str]] = None


# ═══════════ Bookmarks ═══════════

class BookmarkCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=2048)
    description: str = ""
