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
    <html><body style="background:#0d1117;color:#e6edf3;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center"><h2>🚫 注册已关闭</h2><p style="color:#8b949e">这是私有实例，请联系管理员添加账号。</p><p style="margin-top:20px"><a href="/login" style="color:#4fc3f7;text-decoration:none">← 返回登录</a></p></div>
    </body></html>
    """)


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(user: dict | None = Depends(get_optional_user)):
    if not user:
        return HTMLResponse("""
        <html><body style="background:#0d1117;color:#e6edf3;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <div style="text-align:center"><h2>🔒 需要登录</h2><p style="color:#8b949e">请先登录再访问管理面板。</p><p style="margin-top:20px"><a href="/login" style="color:#4fc3f7;text-decoration:none">← 去登录</a></p></div>
        </body></html>
        """)
    admin_path = TEMPLATE_DIR / "admin.html"
    return admin_path.read_text(encoding="utf-8")


@router.get("/translator", response_class=HTMLResponse)
async def translator_page():
    """Universal English↔Chinese translation tool."""
    path = TEMPLATE_DIR / "translator.html"
    return path.read_text(encoding="utf-8")
