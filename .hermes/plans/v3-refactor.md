# ASE Hub v3.0 — 全面重构规划

> 创建: Hermes | 日期: 2026-05-03 | 状态: ⏳ 规划中

---

## 🎯 五大核心问题

| # | 问题 | 严重度 | 影响范围 |
|---|------|--------|----------|
| 1 | 翻译工具 UX 不好用 | 🔴 | 新增的 Glossary 模块 |
| 2 | i18n 不完整 — 翻译/迁移无中文 | 🔴 | 全局用户体验 |
| 3 | 未登录可直接访问 | 🔴 | 安全 |
| 4 | UI 风格不是 Azure 官方风格 | 🟡 | 全局视觉 |
| 5 | 需求分散 — 缺少统一规划 | 🟡 | 开发效率 |

---

## 📋 Issue 1: 翻译工具重设计

### 当前问题
- 只有一个简单的搜索框 + 结果卡片
- 词汇浏览器是平铺的 grid，不够直观
- 缺少"每日一词"、"最近搜索"、"收藏词汇"等功能
- 发音按钮比较简陋

### 目标设计（参考用户图片 + 有道词典/Google Translate 模式）

```
┌──────────────────────────────────────────────────────────┐
│  📖 Azure 术语助手                         [中/EN] [⚙]   │
├──────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │ 🔍 搜索 Azure 术语...                  [🔊 朗读] │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─ 翻译结果 ──────────────────────────────────────┐    │
│  │                                                   │    │
│  │  availability set                  🔊 🇺🇸 🔊 🇬🇧 │    │
│  │  /əˌveɪləˈbɪləti set/                             │    │
│  │                                                   │    │
│  │  可用性集                                         │    │
│  │                                                   │    │
│  │  📂 IaaS → 高可用                                 │    │
│  │  📝 将 VM 放入可用性集可获得 99.95% SLA            │    │
│  │                                                   │    │
│  │  [⭐ 收藏] [📋 复制] [📤 分享]                     │    │
│  └───────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ 相关术语 ──────────────────────────────────────┐    │
│  │  availability zone → 可用性区域                   │    │
│  │  fault domain → 容错域                            │    │
│  │  update domain → 更新域                           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  [📖 全部词汇] [⭐ 我的收藏] [🕐 最近搜索] [🏷 分类]    │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 🔥 热词   │ │ Compute  │ │ Network  │ │ Storage  │   │
│  │ Kubernetes│ │ VM       │ │ VNET     │ │ Blob     │   │
│  │ 容器编排   │ │ 虚拟机    │ │ 虚拟网络  │ │ 对象存储  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 功能清单

| 功能 | 优先级 | 描述 |
|------|--------|------|
| 实时搜索建议 | P0 | 输入时下拉显示匹配项 |
| 丰富结果卡片 | P0 | 音标 + 美/英发音切换 + 例句 + 场景 |
| 相关术语推荐 | P1 | 同场景的其他术语 |
| 收藏词汇 | P1 | 本地存储，个人词汇本 |
| 最近搜索历史 | P1 | 最近 20 条 |
| 分类浏览标签 | P1 | Compute/Network/Storage/... 视觉化分类 |
| 每日一词 | P2 | 首页展示一个随机术语 |
| 热词排行 | P2 | 最常搜索的术语 |

### 交互细节
- 搜索框自动聚焦，Enter 搜索
- 输入时 300ms 防抖，实时显示下拉建议
- 点击建议项直接展示结果
- 🔊 按钮分美式/英式两个
- 收藏按钮有填色动画
- 结果卡片有进入动画 (fadeInUp)

---

## 📋 Issue 2: i18n 完整国际化

### 当前状态
- 部分页面有 `data-i18n` 属性，有中/EN 切换逻辑
- 但以下模块**没有** i18n：
  - ❌ 翻译/Glossary 页面 — 全部硬编码英文
  - ❌ 迁移/Migration 页面 — 全部硬编码英文
  - ❌ 定价表格 Migration 列

### 修复方案

**统一 i18n 架构：**
```javascript
// i18n.js — 全局翻译字典
const I18N = {
  zh: {
    // === 通用 ===
    search: '搜索',
    save: '保存',
    cancel: '取消',
    delete: '删除',
    edit: '编辑',
    loading: '加载中...',
    no_data: '暂无数据',

    // === 导航 ===
    dashboard: '仪表板',
    pricing: '定价查询',
    docs: '文档搜索',
    updates: 'Azure 更新',
    reports: '工作日报',
    meetings: '会议记录',
    glossary: '术语助手',
    snippets: '代码片段',
    migration: '迁移指南',
    admin: '管理面板',

    // === Glossary ===
    search_glossary: '搜索 Azure 术语...',
    pronounce: '发音',
    phonetic: '音标',
    scene: '使用场景',
    example: '例句',
    related_terms: '相关术语',
    my_favorites: '我的收藏',
    recent_searches: '最近搜索',
    all_terms: '全部词汇',
    categories: '分类',
    favorite_added: '已收藏',
    favorite_removed: '已取消收藏',
    us_pronunciation: '美式发音',
    uk_pronunciation: '英式发音',

    // === Migration ===
    migration_guide: '迁移指南',
    cross_subscription: '跨订阅迁移',
    cross_tenant: '跨租户迁移',
    supported: '支持',
    unsupported: '不支持',
    movable: '可迁移',
    cannot_move: '不可迁移',
    best_practices: '最佳实践',
    limitations: '限制说明',
    unsupported_services: '不支持的服务',
    all_services: '全部服务',
    search_services: '搜索服务...',
    check_migration: '检查迁移可行性',

    // === Pricing Migration Column ===
    migration_status: '迁移状态',
    migration_warning: '迁移提醒',
  },
  en: {
    // ... English equivalents
  }
};
```

**需修改的文件：**
| 文件 | 变更 |
|------|------|
| `templates/index.html` | Glossary/Migration 区域加 data-i18n |
| `static/js/glossary.js` | 所有硬编码文字 → `t('key')` |
| `static/js/app.js` | 迁移相关 JS 文字国际化 |
| `static/js/pricing.js` | Migration 列表头国际化 |

---

## 📋 Issue 3: 登录门控

### 问题
访问 `https://ase.hefuzh.com` 直接进入 Dashboard，无需登录。
所有 API 也能匿名访问（除了被保护的 POST 端点）。

### 解决方案

**方案 A：全局登录门控（推荐）**
```python
# middleware in main.py
@app.middleware("http")
async def login_gate(request: Request, call_next):
    # 白名单路径
    PUBLIC_PATHS = [
        "/login", "/api/auth/login", "/api/auth/status",
        "/api/health", "/static/",
    ]
    if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)

    # 检查 session cookie / token
    token = request.cookies.get("ase_token")
    if not token:
        # API 请求返回 401，页面请求重定向到 /login
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        return RedirectResponse(url="/login")

    # 验证 token
    try:
        payload = verify_token(token)
        request.state.user = payload
    except Exception:
        # ... redirect/401
```

**方案 B：仅页面门控**
- 只保护 HTML 页面路由，API 保持现状
- 更简单但不彻底

**推荐方案 A**，实现：
1. 所有非白名单路径需要登录
2. 登录后设置 HttpOnly cookie
3. 无 token 的 API 请求 → 401
4. 无 token 的页面请求 → 重定向到 /login
5. `/static/` 白名单（CSS/JS 需要加载）

---

## 📋 Issue 4: Azure 官方风格 UI

### 参考来源
- [Azure Portal](https://portal.azure.com) 设计语言
- [Fluent UI](https://developer.microsoft.com/fluentui) 组件库
- [Azure Design System](https://azure.microsoft.com/design/)

### 当前 vs 目标

| 元素 | 当前 | Azure 风格目标 |
|------|------|----------------|
| 主色调 | `#0078D4` (类似) | ✅ `#0078D4` Azure Blue |
| 背景 | 深灰 `#1a1a2e` | `#0D1117` Azure Dark |
| 卡片 | 圆角 8px, 半透明 | 圆角 4px, `#1C1E23` 纯色 |
| 侧边栏 | 深色 | Azure Portal 风格折叠侧边栏 |
| 字体 | 系统默认 | Segoe UI / SF Pro |
| 按钮 | 自定义 | Fluent 风格 (边框 + 悬停动画) |
| 输入框 | 简单边框 | Fluent 风格下划线/填充输入 |
| 图标 | Emoji | Fluent Icons (SVG) |
| 顶部导航 | 无 | Azure Portal 风格顶栏 |

### 具体改动

**1. 颜色系统**
```css
:root {
  --azure-blue: #0078D4;
  --azure-blue-hover: #106EBE;
  --azure-dark: #0D1117;
  --azure-card: #1C1E23;
  --azure-border: #2D2F34;
  --azure-text: #F0F0F0;
  --azure-text-secondary: #9CA3AF;
  --azure-success: #22C55E;
  --azure-warning: #F59E0B;
  --azure-danger: #EF4444;
}
```

**2. 组件改造**
- 按钮：Fluent 风格 (padding, border-radius: 2px, focus ring)
- 卡片：Azure Portal 卡片 (flat, darker bg, thinner border)
- 导航：侧边栏 → 可折叠，图标 + 文字
- 输入框：Fluent TextField 风格
- Toast：右上角滑入通知

**3. 布局**
- 顶部状态栏 (Azure 订阅状态 + 用户头像)
- 可折叠侧边栏
- 主内容区更宽的间距

---

## 📋 Issue 5: 开发协作方式

### 分工

| 角色 | 负责 |
|------|------|
| **Hermes (我)** | 架构规划、代码审查、安全检查、部署、GitHub |
| **Claude Code** | 大规模编码：i18n 全站改造、登录门控 Middleware、UI 重构 |

### 执行顺序

```
Phase 1: 安全优先
  ├── 登录门控 (Issue 3) — Hermes 设计 + Claude Code 实现
  └── 审查所有端点权限

Phase 2: i18n 全站
  ├── 统一 i18n 字典 (Hermes 设计)
  ├── 翻译所有硬编码文字 (Claude Code)
  └── Glossary / Migration 中文化 (Claude Code)

Phase 3: 翻译工具重设计
  ├── 新 UI 布局 (Claude Code)
  ├── 搜索建议、收藏、历史 (Claude Code)
  └── 发音双声道切换 (Hermes 后端)

Phase 4: Azure 风格 UI
  ├── 颜色系统 + CSS 变量 (Claude Code)
  ├── 组件库统一 (Claude Code)
  └── 布局调整 (Claude Code)

Phase 5: 测试 + 部署
  ├── 全功能回归测试 (Hermes)
  └── Docker → ACR → VM (Hermes)
```

---

## ⏸️ 待确认

1. **翻译工具参考图** — Claude Code (KIMI 2.6) 无法在本环境分析图片(权限限制)。请用文字描述一下你发的图片里翻译工具的关键特性，或者我可以换个方式。

2. **登录门控范围** — 方案 A（全局门控）还是方案 B（仅页面）？

3. **Azure 风格** — 是否需要引入 Fluent UI 组件库，还是纯 CSS 模仿即可？（推荐纯 CSS，保持轻量）

---

## 📊 预估工作量

| Phase | 预估时间 | 复杂度 |
|-------|----------|--------|
| 1. 登录门控 | 30min | ⭐⭐ |
| 2. i18n | 45min | ⭐⭐⭐ |
| 3. 翻译重设计 | 60min | ⭐⭐⭐⭐ |
| 4. Azure UI | 90min | ⭐⭐⭐⭐ |
| 5. 测试部署 | 30min | ⭐⭐ |
| **总计** | **~4h** | |

---

*下一步：等你确认上述方向，我分配 Claude Code 开始 Phase 1。*
