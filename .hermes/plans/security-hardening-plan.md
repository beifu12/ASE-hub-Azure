# ASE Hub v2.1 Security Hardening Plan

> P0: Security | P1: Reliability | P2: UX
> Agents: Hermes (orchestration) + Claude Code (implementation)

---

## P0.1 — CORS 加固

**文件:** `app/main.py`
**改动:** 添加 CORSMiddleware，只允许 `https://ase.hefuzh.com`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ase.hefuzh.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## P0.2 — Pydantic 请求校验

**文件:** `app/schemas.py` (新建) + `app/routes/api.py` (修改)

创建所有请求/响应的 Pydantic 模型：
- `LoginRequest(username, password)`
- `ReportCreate(date, project, tasks, blockers, next_steps)`
- `MeetingCreate(title, date, attendees, notes, action_items)`
- `BookmarkCreate(title, url, description)`
- `AdminCreateUser(username, password, display_name)`

所有 `request.json()` → Pydantic model parse

---

## P0.3 — Health Check 强化

**文件:** `app/main.py` 或新建 `app/services/health.py` (修改)

```python
@router.get("/health")
async def api_health(db: AsyncSession = Depends(get_db)):
    db_ok = False
    try:
        await db.execute(select(1))
        db_ok = True
    except: pass
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "service": "ASE Hub",
        "version": "2.1.0"
    }
```

---

## P0.4 — 登录速率限制

**文件:** `app/middleware.py` (新建)
**依赖:** 无需额外包，用内存字典实现简单限流

```python
from collections import defaultdict
import time

login_attempts = defaultdict(list)  # {ip: [timestamp, ...]}

async def rate_limit_login(request: Request, call_next):
    if request.url.path == "/api/auth/login":
        ip = request.client.host
        now = time.time()
        attempts = [t for t in login_attempts[ip] if now - t < 60]
        if len(attempts) >= 5:
            raise HTTPException(429, "Too many login attempts. Try again in 1 minute.")
        attempts.append(now)
        login_attempts[ip] = attempts
    return await call_next(request)
```

---

## P0.5 — 定价 Migration 列 JS 逻辑

**文件:** `app/static/js/pricing.js`
**改动:** 在渲染表格时，调用 `/api/migration/check?service=...` 或直接匹配 migration 数据，在 Migration 列显示 ✅/⚠️ 图标

---

## P0.6 — 报告/会议编辑和删除

**文件:** `app/services/reports.py`, `app/services/meetings.py`, `app/routes/api.py`

新增端点:
- `PUT /api/reports/{report_id}` — 编辑报告
- `DELETE /api/reports/{report_id}` — 删除报告
- `PUT /api/meetings/{meeting_id}` — 编辑会议
- `DELETE /api/meetings/{meeting_id}` — 删除会议

前端添加编辑/删除按钮

---

## P0.7 — 异常处理统一

**文件:** `app/main.py`
**改动:** 添加全局异常处理器

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## 执行分工

| 任务 | Agent | 预估 |
|------|-------|------|
| P0.1 CORS | Hermes | 3 min |
| P0.2 Pydantic | Claude Code | 15 min |
| P0.3 Health DB | Hermes | 3 min |
| P0.4 Rate Limit | Claude Code | 10 min |
| P0.5 Pricing JS | Hermes | 10 min |
| P0.6 Edit/Delete | Claude Code | 20 min |
| P0.7 Error Handler | Hermes | 2 min |
