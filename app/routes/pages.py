from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from app.auth import get_optional_user
from fastapi import Depends, Request

router = APIRouter()

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


@router.get("/", response_class=HTMLResponse)
async def home(user: dict | None = Depends(get_optional_user)):
    index_path = TEMPLATE_DIR / "index.html"
    html = index_path.read_text(encoding="utf-8")
    return html


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    login_path = TEMPLATE_DIR / "login.html"
    return login_path.read_text(encoding="utf-8")


@router.get("/register", response_class=HTMLResponse)
async def register_page():
    reg_path = TEMPLATE_DIR / "register.html"
    return reg_path.read_text(encoding="utf-8")
