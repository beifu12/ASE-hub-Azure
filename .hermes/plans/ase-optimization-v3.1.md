# ASE Hub v3.1 拓展优化计划

**审计日期**: 2026-05-03  
**当前版本**: v3.0.0  
**目标版本**: v3.1.0  

## 审计发现

| 模块 | 文件数 | 总行数 | 问题 |
|------|--------|--------|------|
| Python 后端 | 28 | 1,767 | 重复CRUD模式、同步HTTP阻塞、翻译无缓存 |
| JS 前端 | 9 | 1,372 | 9个独立文件、无压缩 |
| CSS | 10 | 1,089 | 10个独立文件、无压缩 |
| HTML | 5 | 1,265 | translator.html 冗余 (已废弃) |

## 当前架构

```
┌────────────────────────────────────────────────────┐
│                  Cloudflare CDN                     │
│           (CSS/JS HIT 4h, HTML DYNAMIC)            │
├────────────────────────────────────────────────────┤
│               Azure VM (eastasia)                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  Docker Container (python:3.12-slim)         │  │
│  │  ┌──────────────────────────────────────────┐│  │
│  │  │  FastAPI + uvicorn (单进程)              ││  │
│  │  │  ├─ Middleware: rate-limit + login gate  ││  │
│  │  │  ├─ Auth: JWT + bcrypt (multi-user)      ││  │
│  │  │  ├─ DB: SQLite async (per-request pool)  ││  │
│  │  │  ├─ Services:                            ││  │
│  │  │  │  reports/meetings (95%重复)          ││  │
│  │  │  │  pricing/docs/updates/health          ││  │
│  │  │  │  translator + universal_translator    ││  │
│  │  │  │  snippets/bookmarks/migration         ││  │
│  │  │  └─ Cache: TTLCache (pricing/updates/health)│  │
│  │  └──────────────────────────────────────────┘  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

## 优化计划 (4个优先级)

### P0 🔴 前端性能 — 首屏加速

| # | 任务 | 文件 | 预期效果 |
|---|------|------|---------|
| P0-1 | CSS 合并为 2 文件 (critical.css + deferred.css) | 10→2 | -8 HTTP请求 |
| P0-2 | JS 合并为 2 文件 (vendor.js + app.js) | 9→2 | -7 HTTP请求 |
| P0-3 | 首屏关键CSS内联到 index.html `<style>` | index.html | FCP -0.5s |
| P0-4 | 非关键JS 加 defer/async | index.html | TTI -0.3s |
| P0-5 | 删除废弃 translator.html | templates/ | 清理 |
| P0-6 | Cloudflare 缓存规则优化: index.html 缓存 5min | Cloudflare | 减少源服务器负载 |

**预期**: 首次加载从 19 HTTP请求 → 4 HTTP请求，FCP 从 ~1.5s → ~0.8s

### P1 🟡 后端性能

| # | 任务 | 文件 | 预期效果 |
|---|------|------|---------|
| P1-1 | DB 连接池从 per-request 改为全局池 | database.py | 减少连接开销 |
| P1-2 | universal_translator 加 TTLCache (10min) | universal_translator.py | API调用 -80% |
| P1-3 | translator.py 同步改为异步 (httpx → httpx.AsyncClient) | translator.py | 不再阻塞事件循环 |
| P1-4 | seed_snippets 从 main.py 移到配置文件 | main.py + data/ | 减少启动复杂度 |
| P1-5 | 全局 exception handler 加日志 | main.py | 可观测性 |

### P2 🟢 代码质量

| # | 任务 | 文件 | 预期效果 |
|---|------|------|---------|
| P2-1 | 抽取 BaseCRUDService 基类，消除 reports/meetings/bookmarks 重复 | 新建 + services/*.py | -200行重复代码 |
| P2-2 | 统一翻译入口 → 单一 TranslationService | translator.py + universal_translator.py | -1文件 |
| P2-3 | updates.py categories_map 去重 | updates.py | -30行 |
| P2-4 | api.py 瘦身 → 拆分为独立路由文件 | routes/api.py → routes/auth.py, routes/data.py | 可维护性 |

### P3 🔵 部署运维

| # | 任务 | 文件 | 预期效果 |
|---|------|------|---------|
| P3-1 | Dockerfile 多阶段构建 | Dockerfile | 镜像 -40% |
| P3-2 | uvicorn 单进程 → gunicorn + uvicorn workers (2 workers) | Dockerfile + CMD | 并发提升 |
| P3-3 | 健康检查端点加强 (DB + 磁盘) | main.py | 监控 |
| P3-4 | requirements.txt 整理 (去未使用依赖) | requirements.txt | 镜像缩小 |

## 任务分配

根据团队规则:
- **Hermes (我)**: 架构设计、计划编写、代码审查、部署协调
- **Claude Code**: 所有编码执行 (P0-1~P0-6, P1-1~P1-5, P2-1~P2-4, P3-1~P3-4)
- **OpenClaw (洛琪希)**: 集成测试、API验证、部署后健康检查

## 执行顺序

```
Phase 1 (P0) — 前端优化                      Claude Code
    ↓ 部署验证
Phase 2 (P1) — 后端优化                      Claude Code
    ↓ 集成测试
Phase 3 (洛琪希) — API测试 + 健康检查         OpenClaw
    ↓
Phase 4 (P2) — 代码质量重构                  Claude Code
    ↓
Phase 5 (P3) — 部署优化                      Claude Code
    ↓
Phase 6 (洛琪希) — 最终验收测试               OpenClaw
```
