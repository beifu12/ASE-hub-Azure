# ASE Hub v3 — 架构分析与执行计划

> Hermes 编写 | 2026-05-03 | 基于完整代码审查

---

## 📊 代码库概况

```
总文件: 40 files  |  总代码: 2,936 LOC  |  注释: 358 lines (8.1%)

Python    20 files   999 LOC  65%  ← 后端主力
HTML       3 files   527 LOC  88%  ← 模板
CSS        1 file    488 LOC  74%  ← 全局样式
JS         7 files   784 LOC  70%  ← 前端逻辑
Docker     1 file    11 LOC        ← 容器化
```

**架构模式**: 单体 FastAPI + SPA (无框架) + SQLite + Docker

---

## 🏗️ 当前架构

```
┌─────────────────────────────────────────────────────────────┐
│  Cloudflare (SSL Termination)                                │
│  ase.hefuzh.com → Azure VM 20.24.64.57:8000                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Docker: ase-hub (python:3.12-slim)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI app (main.py)                  v2.4.0        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │  │
│  │  │ CORS MW  │→│Rate Limit│→│ Login Gate MW    │    │  │
│  │  └──────────┘ └──────────┘ └──────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  Routes                                      │  │  │
│  │  │  ├─ api.py  (20+ endpoints, 316 lines)       │  │  │
│  │  │  └─ pages.py (HTML views, login/admin)       │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │  Services (10 modules)                       │  │  │
│  │  │  pricing docs updates health                 │  │  │
│  │  │  reports meetings snippets migration         │  │  │
│  │  │  translator tts_service                      │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │ database │ │  auth    │ │ models   │          │  │
│  │  │ SQLite   │ │  JWT     │ │ SQLAlch  │          │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  │  ┌──────────────────────────────────────────┐    │  │
│  │  │  Static: JS(7)+CSS(1)+Audio(2)           │    │  │
│  │  └──────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ 架构问题诊断

### 🔴 严重 (影响安全/可靠性)

| # | 问题 | 位置 | 影响 |
|---|------|------|------|
| 1 | **无自动化测试** | 全项目 | 改代码全靠手工 curl，回归风险高 |
| 2 | **无结构化日志** | 全项目 | 出问题只能看 uvicorn access log |
| 3 | **无健康检查详情** | `api.py:health` | 只返回 DB 状态，不检查 Azure API 连通性 |
| 4 | **全局 except 吞异常** | `main.py:64` | 500 统一返回 "Internal server error"，无法定位问题 |
| 5 | **无 CI/CD** | 无 `.github/workflows/` | 每次手动 docker build/push/deploy |

### 🟡 中等 (影响可维护性/体验)

| # | 问题 | 位置 | 影响 |
|---|------|------|------|
| 6 | **CSS 单一文件膨胀** | `style.css` 488 行 | 难以维护，样式冲突风险 |
| 7 | **JS 全局函数污染** | 所有 `*.js` | 函数全挂 window，命名冲突风险 |
| 8 | **无前端构建工具** | 静态 JS | 无 minify/bundle/cache-busting |
| 9 | **i18n 不完整** | Migration/Pricing | 部分区域仍硬编码英文 |
| 10 | **无 API 文档** | FastAPI 自带 | `openapi.json` 存在但无自定义描述 |
| 11 | **services 返回不一致** | `services/*.py` | 有的用 async session，有的用 dict，混用 |

### 🟢 低优先级 (体验优化)

| # | 问题 | 位置 |
|---|------|------|
| 12 | 无暗色/亮色主题切换 | `style.css` |
| 13 | 无分页（glossary 200+ 条一次加载） | `translator.py` |
| 14 | 无 mobile 响应式优化 | 全局 |
| 15 | 无键盘快捷键 | `app.js` |
| 16 | 无离线 PWA 支持 | 无 manifest |

---

## 🛠️ 可搭配的现有 Skills

| Skill | 用途 | 状态 |
|-------|------|------|
| **architecture-diagram** | 生成 ASE Hub 架构图（SVG/HTML） | ✅ 可用 |
| **azure-landing-zone** | Terraform 部署模式、Docker on Azure 最佳实践 | ✅ 已实施 |
| **fastapi-multiuser-auth** | JWT 多用户模式参考 | ✅ 已实施 |
| **requesting-code-review** | 代码审查、安全检查 | ✅ 可用 |
| **test-driven-development** | TDD 流程，先写测试 | ⚠️ 需要 |
| **writing-plans** | 结构化实施计划 | ✅ 本文即用 |
| **hermes-agent-skill-authoring** | 可为重复操作创建 Skill | 🔧 后续 |

---

## 🎯 Phase 4: Azure UI 改造 — 详细分解

### 4.1 颜色系统 (影响全局)

```css
:root {
  /* 主色 */
  --accent: #0078D4;              /* Azure Blue */
  --accent-hover: #106EBE;

  /* 背景 */
  --bg-primary: #0D1117;          /* Azure Dark */
  --bg-secondary: #161B22;        /* Card bg */
  --bg-card: #1C1E23;             /* Elevated card */

  /* 边框 */
  --border: #30363D;              /* Subtle border */

  /* 文字 */
  --text-primary: #E6EDF3;        /* Main text */
  --text-secondary: #8B949E;      /* Secondary */
  --text-muted: #484F58;          /* Muted */

  /* 功能色 */
  --success: #238636;
  --warning: #D29922;
  --danger: #DA3633;

  /* 字体 */
  --font-sans: 'Segoe UI', -apple-system, sans-serif;
  --font-mono: 'Cascadia Code', 'Fira Code', monospace;

  /* 圆角 (Azure 风格更方正) */
  --radius: 4px;
}
```

### 4.2 组件改造

| 组件 | 当前 | 目标 |
|------|------|------|
| 按钮 | 圆角 6px | Fluent: 2px 圆角, 聚焦环, hover 位移 |
| 卡片 | 半透明 + 大圆角 | 纯色 + 4px 圆角 + 细边框 |
| 输入框 | 简单边框 | Fluent underline style |
| 侧边栏 | 固定展开 | 可折叠 + 图标模式 |
| Toast | 居中底部 | 右上角滑入 |
| 表格 | 简单 | 斑马纹 + hover 高亮 |

### 4.3 新增: 顶部状态栏

```
┌──────────────────────────────────────────────────────────────┐
│ 🟢 Azure: OK  |  East Asia  |  👤 admin  |  🌐 中/EN  | ⚙  │
└──────────────────────────────────────────────────────────────┘
```

### 4.4 新增: 可折叠侧边栏

```css
.sidebar.collapsed { width: 56px; }
.sidebar.collapsed .nav-item span:not(.icon) { display: none; }
.sidebar.collapsed .nav-item .icon { font-size: 20px; }
```

### 4.5 Files to change

| 文件 | 行数 | 改动量 |
|------|------|--------|
| `static/css/style.css` | 488 | 全文重构 ~300 行受影响的变量 |
| `templates/index.html` | 363 | 侧边栏结构调整 + 顶栏 |
| `templates/login.html` | ? | 配色统一 |
| `templates/admin.html` | ? | 配色统一 |
| `static/js/app.js` | 349 | 侧边栏折叠逻辑 |

---

## 🔄 执行顺序 (推荐)

```
Phase 4a: 颜色系统变量替换      ← 30min, 低风险, 纯 CSS
    ↓
Phase 4b: 组件样式统一          ← 30min, 中风险
    ↓
Phase 4c: 侧边栏折叠 + 顶栏      ← 30min, 需改 HTML+JS
    ↓
Phase 5:  自动化测试             ← 45min, pytest + CI
    ↓
Phase 6:  售前工具               ← 架构图/POC清单/方案模板
```

### 为什么这个顺序？

1. **4a 颜色先做** — 纯 CSS 变量替换，改动最小，视觉变化最大
2. **4b 组件** — 依赖 4a 的颜色变量
3. **4c 交互** — 等 4b 的组件稳定后加折叠
4. **5 测试** — UI 稳定后再加测试
5. **6 售前工具** — 新功能，最后加

---

## 🎯 售前工具路线图 (Phase 6)

可用的 skills:
| 工具 | 实现方式 | 需要 Skill |
|------|----------|-----------|
| 架构图生成 | `architecture-diagram` skill → SVG | ✅ 已有 |
| POC 清单 | 模板 + 选择题 → 生成 Markdown | 🔧 新建 |
| 方案模板 | 结构化表单 → 生成文档 | 🔧 新建 |

---

## 📋 当前可立即开始

**Phase 4a — 颜色系统替换**
- 影响文件: `style.css` (约 30 处变量值)
- 风险: ⭐ (低，仅 CSS)
- 时间: ~20min
- 可回滚: `git checkout style.css`

**开始前确认**: 是否保持暗色主题，还是增加亮/暗切换？
