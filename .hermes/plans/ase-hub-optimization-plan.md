# ASE Hub 优化拓展 — 实施计划

> **For Hermes:** 使用 subagent-driven-development skill 执行此计划，结合 Claude Code + OpenClaw 并行。

**目标:** ASE Hub 数据层 SQLite 化 + 跨订阅迁移智能提醒 + 缓存 + 前端现代化

**架构:** FastAPI + SQLAlchemy/SQLite 替代 JSON 文件; 迁移知识库 JSON → API → 前端智能提醒; cachetools 缓存层; Vite 打包前端

**三 Agent 分工:**

| Agent | 角色 | 负责模块 |
|-------|------|----------|
| Hermes (艾莉丝) | 编排总控 | 计划审查、任务分派、最终集成审查 |
| Claude Code | 编码主力 | SQLite 迁移、迁移知识库、前端集成 |
| OpenClaw (洛琪希) | 工具执行 | 缓存层、Vite 配置、速率限制、验证 |

---

## Phase 1: 数据层 SQLite 迁移（Claude Code）

### Task 1.1: 安装 SQLAlchemy 依赖

**目标:** 添加 SQLAlchemy + aiosqlite 到 requirements.txt

**文件:**
- Modify: `requirements.txt`

**内容:**
```
# 新增依赖
sqlalchemy[asyncio]==2.0.36
aiosqlite==0.20.0
```

### Task 1.2: 创建数据库模型层

**目标:** 创建 SQLAlchemy 模型，替换 JSON 文件存储

**文件:**
- Create: `app/database.py` — SQLAlchemy 引擎 + Base + 会话工厂
- Create: `app/models.py` — User, Report, Meeting, Bookmark, Snippet 模型

**模型设计:**
```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./data/ase_hub.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
```

```python
# app/models.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
import uuid

def gen_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: gen_id("usr_"))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=lambda: gen_id("rpt_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    project = Column(String, default="")
    tasks = Column(JSON, default=list)
    blockers = Column(Text, default="")
    next_steps = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(String, primary_key=True, default=lambda: gen_id("mtg_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="")
    date = Column(String, nullable=False)
    attendees = Column(JSON, default=list)
    notes = Column(Text, default="")
    action_items = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(String, primary_key=True, default=lambda: gen_id("bm_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
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
    user_id = Column(String, default="shared")
```

### Task 1.3: 重构 auth.py 使用 SQLAlchemy

**目标:** 将 users.json 文件操作改为 SQLAlchemy 异步查询

**文件:**
- Modify: `app/auth.py`

**关键改动:**
- `_load_users()` → async query `User` 表
- `create_user()` → async insert `User` 行
- `authenticate_user()` → async query + bcrypt 验证

### Task 1.4: 重构 services 使用 SQLAlchemy

**目标:** 将所有 JSON 文件 CRUD 改为 SQLAlchemy 异步操作

**文件:**
- Modify: `app/services/reports.py`
- Modify: `app/services/meetings.py`
- Modify: `app/services/snippets.py`
- Modify: `app/routes/api.py` (bookmarks 部分)

### Task 1.5: 更新 FastAPI 启动流程

**目标:** 在应用启动时初始化数据库 + 插入默认数据

**文件:**
- Modify: `app/main.py`

```python
from contextlib import asynccontextmanager
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="ASE Hub", version="2.0.0", lifespan=lifespan)
```

### Task 1.6: 数据迁移脚本（JSON → SQLite）

**目标:** 将现有的 users.json / reports.json / meetings.json 迁移到 SQLite

**文件:**
- Create: `scripts/migrate_json_to_sqlite.py`

---

## Phase 2: 缓存策略（OpenClaw）

### Task 2.1: 添加缓存依赖

```
cachetools==5.5.0
```

### Task 2.2: 创建缓存装饰器

**文件:**
- Create: `app/cache.py`

```python
from cachetools import TTLCache
from functools import wraps
import asyncio

# Pricing 缓存: 最多 200 条, 10 分钟 TTL
pricing_cache = TTLCache(maxsize=200, ttl=600)

# Updates 缓存: 1 小时 TTL
updates_cache = TTLCache(maxsize=10, ttl=3600)

# Health 缓存: 5 分钟 TTL
health_cache = TTLCache(maxsize=10, ttl=300)

def cached(cache_dict, key_fn=None):
    """异步缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_fn(*args, **kwargs) if key_fn else str(args) + str(kwargs)
            if key in cache_dict:
                return cache_dict[key]
            result = await func(*args, **kwargs)
            cache_dict[key] = result
            return result
        return wrapper
    return decorator
```

### Task 2.3: 为服务添加缓存

**文件:**
- Modify: `app/services/pricing.py` — 添加 `@cached(pricing_cache, key_fn=...)`
- Modify: `app/services/updates.py` — 添加 `@cached(updates_cache)`
- Modify: `app/services/health.py` — 添加 `@cached(health_cache)`

---

## Phase 3: 跨订阅迁移知识库（Claude Code）

### Task 3.1: 迁移知识数据文件

**目标:** 创建覆盖 60+ Azure 服务的迁移支持状态数据

**文件:**
- Create: `app/data/migration_kb.json`

**数据结构:**
```json
[
  {
    "serviceName": "Virtual Machines",
    "crossSubscriptionMove": true,
    "crossTenantMove": false,
    "notes": "支持的资源类型: VM + 托管磁盘 + NIC。需在同一区域。",
    "restrictions": [
      "必须移动所有依赖资源（磁盘、NIC、公网 IP）",
      "可用性集中的 VM 需全部移动",
      "目标订阅需有足够配额"
    ],
    "bestPractices": [
      "移动前创建快照备份",
      "验证目标区域配额",
      "使用 Azure Resource Mover 进行规划"
    ],
    "officialDoc": "https://learn.microsoft.com/azure/azure-resource-manager/management/move-support-resources",
    "categories": ["compute"]
  },
  ...
]
```

### Task 3.2: 迁移知识 API

**文件:**
- Create: `app/services/migration.py`
- Modify: `app/routes/api.py` — 添加新端点

**API 端点:**
```python
# GET /api/migration/services — 列出所有有迁移限制的服务
# GET /api/migration/check?service=Virtual Machines — 查特定服务
# GET /api/migration/search?keyword=VM — 模糊搜索
```

### Task 3.3: 搜索联动（智能提醒）

**目标:** 在 pricing 搜索结果中注入迁移提醒

**文件:**
- Modify: `app/services/pricing.py` — 搜索时同时查询迁移知识库，附加 `migrationWarning` 字段

---

## Phase 4: 前端现代化（OpenClaw）

### Task 4.1: Vite 项目初始化

**目标:** 在项目根目录设置 Vite 打包

**文件:**
- Create: `package.json`
- Create: `vite.config.js`
```js
import { defineConfig } from 'vite'
export default defineConfig({
  root: 'frontend',
  build: { outDir: '../app/static/dist', emptyOutDir: true },
})
```

### Task 4.2: 前端模块化拆分

**目标:** 将 JS 模块改为 ES modules

**文件:**
- Move: `app/static/js/*.js` → `frontend/js/*.js`
- Add ES module `import/export` 语句

### Task 4.3: 骨架屏 + 错误 UX 优化

**文件:**
- Modify: `frontend/js/pricing.js` — 加载骨架屏
- Modify: `frontend/js/dashboard.js` — 错误 toast 改进

---

## Phase 5: 安全增强（OpenClaw）

### Task 5.1: 速率限制

**文件:**
- Create: `app/middleware.py`

```python
# 使用 slowapi 或手动实现基础速率限制
# POST /api/auth/register: 5 requests/minute
# POST /api/auth/login: 10 requests/minute
```

### Task 5.2: CORS 强化

**文件:**
- Modify: `app/main.py`

---

## Phase 6: 集成测试验证（Hermes + 双方审查）

### Task 6.1: 全栈测试

- 启动本地 FastAPI + SQLite
- 验证所有 API 端点
- 验证迁移知识 API
- 验证缓存命中
- 验证前端打包

---

## 执行顺序

```
Phase 1 (Claude Code) ──→ Phase 2 (OpenClaw) 并行
                                    ↓
Phase 3 (Claude Code) ──→ Phase 4 (OpenClaw) 并行
                                    ↓
Phase 5 (OpenClaw) ──→ Phase 6 (Hermes 审查)
```

**注意:** Phase 1 必须先完成（Phase 2-6 依赖 SQLAlchemy 迁移），其余可最大化并行。
