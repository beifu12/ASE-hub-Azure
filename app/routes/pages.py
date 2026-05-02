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
    return HTMLResponse("""
    <html><body style="background:#1a1a2e;color:#e0e0e0;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center"><h2>🚫 注册已关闭</h2><p>这是私有实例，请联系管理员。</p><p><a href="/login" style="color:#4fc3f7">返回登录</a></p></div>
    </body></html>
    """)


@router.get("/admin", response_class=HTMLResponse)
async def admin_page():
    admin_path = TEMPLATE_DIR / "admin.html"
    return admin_path.read_text(encoding="utf-8")
