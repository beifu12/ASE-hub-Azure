# 🏗️ ASE Hub — Azure Solutions Engineer Hub

[![Deploy](https://img.shields.io/badge/deploy-ASE%20Hub-blue)](https://ase.hefuzh.com)
[![Version](https://img.shields.io/badge/version-3.0.0-blue)](https://github.com/beifu12/ASE-hub-Azure)
[![CI](https://img.shields.io/badge/CI-pytest-brightgreen)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A self-hosted **Azure Portal-style dashboard** for Azure Solutions Engineers — pricing lookup, documentation search, update feeds, work reports, meeting summaries, CLI cheat sheets, **cross-subscription migration intelligence**, and **Blade slide-in panels**.

> **Live:** https://ase.hefuzh.com

![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoft-azure&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)

---

## ✨ Features

| Module | Description |
|---|---|
| 📊 **Dashboard Tile Grid** | 7 Azure Portal-style tiles — status, VM info, user count, service health, updates, quick links, bookmarks |
| 🔲 **Blade Panels** | Azure Portal-style slide-in detail panels (open from tiles, ESC to close) |
| 💰 **Pricing** | Search Azure Retail Prices API with **migration warnings** |
| 🔄 **Migration Guide** | 70+ Azure services — cross-subscription move support, restrictions, best practices |
| 📚 **Docs** | Search Microsoft Azure documentation |
| 📡 **Updates** | RSS feed from Azure updates, filterable by category |
| 📝 **Reports** | Daily work reports with Markdown export |
| 🤝 **Meetings** | Meeting summaries with action items & Markdown export |
| ⚡ **Snippets** | Azure CLI & Bicep cheat sheets (12+ built-in snippets) |
| 🔖 **Bookmarks** | Save useful Azure links |
| ⚙️ **Admin Panel** | User management — add/remove accounts via web UI |
| 🧪 **CI/CD** | GitHub Actions + pytest (7 tests, automated on push/PR) |

### 🔐 Authentication

- **JWT-based login** (bcrypt password hashing, HS256 tokens)
- **Per-user data isolation** — reports, meetings, bookmarks scoped to user
- **Private instance mode** — registration disabled; admin adds users manually
- Token auto-refresh, logout, 401 auto-redirect

### 🔄 Cross-Subscription Migration Intelligence

When searching Azure pricing, each result now includes a `migrationWarning` field:

- **ℹ️ Supported** — service supports cross-subscription move with best practices
- **⚠️ Restricted** — service does NOT support cross-subscription move, with migration notes

Dedicated API for SA workflow:
- `GET /api/migration/services` — browse all 70+ services
- `GET /api/migration/check?service=Key Vault` — check specific service
- `GET /api/migration/search?keyword=VM` — fuzzy search

### ⚡ Caching

- Pricing results: 10-minute TTL (TTLCache, 200 entries)
- Azure updates RSS: 1-hour TTL
- Service health: 5-minute TTL

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development

```bash
git clone https://github.com/beifu12/ASE-hub-Azure.git
cd ASE-hub-Azure

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create admin account
python scripts/create_admin.py admin YourPassword "Display Name"

# Run
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 → login → http://localhost:8000/admin to manage users.

### Docker

```bash
docker build -t ase-hub .
docker run -d --name ase-hub -p 8000:8000 -v $(pwd)/data:/app/data ase-hub

# Create admin inside container
docker exec -it ase-hub python scripts/create_admin.py admin YourPassword
```

### Azure Deployment

```bash
cd terraform
terraform init
terraform apply  # edit terraform.tfvars first
```

Creates: ACR → VNet → VM (Ubuntu 24.04 + Docker) → NSG (HTTP/SSH) → Managed Identity (ACR pull)

---

## 📁 Project Structure

```
ase-hub/
├── app/
│   ├── main.py              # FastAPI entry point (v2.0.0, SQLAlchemy lifespan)
│   ├── database.py          # SQLAlchemy async engine + session factory
│   ├── models.py            # ORM models (User, Report, Meeting, Bookmark, Snippet)
│   ├── auth.py              # JWT auth, bcrypt, FastAPI dependencies
│   ├── cache.py             # cachetools TTLCache (pricing/updates/health)
│   ├── routes/
│   │   ├── api.py           # All API endpoints (auth/admin/public/migration/protected)
│   │   └── pages.py         # Page routes (/, /login, /register, /admin)
│   ├── services/
│   │   ├── pricing.py       # Azure Retail Prices API + migration warnings
│   │   ├── migration.py     # Cross-subscription migration knowledge base
│   │   ├── docs.py          # Azure documentation search
│   │   ├── updates.py       # Azure updates RSS feed (cached)
│   │   ├── health.py        # Azure service health (cached)
│   │   ├── reports.py       # Work reports CRUD (SQLAlchemy)
│   │   ├── meetings.py      # Meeting summaries CRUD (SQLAlchemy)
│   │   └── snippets.py      # CLI/Bicep cheat sheets (SQLAlchemy)
│   ├── data/
│   │   └── migration_kb.json  # 70 Azure services migration data
│   ├── templates/
│   │   ├── index.html       # Main dashboard (3-column tile grid + blade panel)
│   │   ├── login.html       # Login page
│   │   ├── register.html    # Registration (disabled — redirect to admin)
│   │   └── admin.html       # Admin user management panel
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css        # CSS variables, reset, typography
│   │   │   ├── components.css  # Buttons, inputs, cards, toggles, modals
│   │   │   ├── topbar.css      # Top navigation bar
│   │   │   ├── sidebar.css     # Collapsible sidebar with groups
│   │   │   ├── breadcrumb.css  # Breadcrumb navigation
│   │   │   ├── tiles.css       # Dashboard tile grid (1x1, 2x1, 3x1)
│   │   │   ├── blade.css       # Slide-in blade panel (Azure Portal style)
│   │   │   ├── glossary.css    # Glossary terms
│   │   │   ├── responsive.css  # Mobile responsive breakpoints
│   │   │   └── style.css       # Legacy (kept for backward compat)
│   │   └── js/
│   │       ├── app.js, dashboard.js, nav.js   # Core dashboard
│   │       ├── blade.js       # Blade panel open/close + ESC key
│   │       ├── pricing.js, docs.js, glossary.js, reports.js, meetings.js
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py        # Fixtures: TestClient, in-memory SQLite, admin user
│   │   └── test_api.py        # 7 tests: health, login, unauthorized, translate, status, updates
├── scripts/
│   ├── create_admin.py      # CLI: create initial admin user
│   └── migrate_json_to_sqlite.py  # One-off: migrate old JSON data → SQLite
├── terraform/               # Azure infrastructure as code
├── data/                    # Runtime data (gitignored) — SQLite DB + JWT secret
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## 🔧 API Endpoints

### Public (no auth)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/auth/status` | Auth status (registration: closed) |
| GET | `/api/pricing?keyword=vm&region=eastasia` | Pricing search (+ migration warnings) |
| GET | `/api/docs?q=functions` | Azure docs search |
| GET | `/api/updates?category=compute` | Azure updates RSS (cached) |
| GET | `/api/status` | Azure service health (cached) |

### Migration Guide (no auth)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/migration/services` | All 70 services with move status |
| GET | `/api/migration/services?unsupported_only=true` | Only unmovable services |
| GET | `/api/migration/check?service=Key+Vault` | Check specific service |
| GET | `/api/migration/search?keyword=VM` | Fuzzy search |

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | ❌ Disabled (private instance) |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user info |

### Admin (requires JWT)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/users` | List all users |
| POST | `/api/admin/users` | Create user |
| DELETE | `/api/admin/users/{id}` | Delete user (not self) |

### Protected (requires JWT)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports` | List user's reports |
| POST | `/api/reports` | Create report |
| GET | `/api/meetings` | List user's meetings |
| POST | `/api/meetings` | Create meeting |
| GET | `/api/snippets` | List snippets |
| GET/POST | `/api/bookmarks` | User bookmarks |

---

## 🛡️ Security

- Passwords hashed with **bcrypt**
- JWT tokens (HS256) signed with auto-generated secret
- User data isolated — per-user reports, meetings, bookmarks
- Registration **disabled by default** — admin adds users
- `data/` directory excluded from git
- Rate limiting ready (Phase 5)

---

## 🎨 Tech Stack

- **Backend:** FastAPI, Uvicorn, SQLAlchemy 2.0 (async), aiosqlite
- **Auth:** JWT (python-jose), bcrypt
- **Cache:** cachetools (TTLCache)
- **API Clients:** httpx, feedparser
- **Frontend:** Vanilla JS, CSS (Azure dark theme, componentized 10 files)
- **Database:** SQLite (WAL mode)
- **Testing:** pytest + GitHub Actions CI
- **Infra:** Terraform, Docker, Azure VM + ACR
- **CDN/Proxy:** Cloudflare

---

## 📝 Changelog

### v3.0.0 (2026-05-02) — Azure Portal Dashboard
- **Blade panels:** Slide-in detail panels (Azure Portal style), ESC to close
- **CSS componentization:** 10 modular CSS files (base, components, topbar, sidebar, breadcrumb, tiles, blade, glossary, responsive, legacy)
- **CI/CD:** GitHub Actions pipeline + pytest (7 tests: health, auth, endpoints)
- **Testing:** In-memory SQLite fixtures, JWT-authenticated API tests
- **Tile Grid v3:** 7 tiles (1x1/2x1), BEM naming, status borders, mobile responsive

### v2.7.0 (2026-05-02) — Dashboard Tile Grid
- **Tile layout:** 7 tiles in 3-column CSS Grid — system status, VM info, user count, service health (2-col), updates (2-col), quick links, bookmarks
- **Dashboard.js rewrite:** JavaScript-driven tile rendering with API integration
- **Status borders:** Tile border colors — green (ok), yellow (warning), red (error)
- **Mobile responsive:** Single-column layout on small screens

### v2.6.0 (2026-05-02) — Navigation Overhaul
- **Topbar:** Azure-style top navigation bar with hamburger toggle
- **Sidebar:** Collapsible sidebar with grouped sections, collapse/expand state persistence
- **Breadcrumb:** Dynamic breadcrumb navigation
- **nav.js:** Centralized navigation logic — `navigateTo()`, recent tracking, localStorage persistence

### v2.5.0 (2026-05-02) — Azure Fluent Design
- **Azure dark theme:** Background `#0D1117`, cards `#161B22`, primary `#0078D4`, 4px border-radius
- **Fluent components:** Focus rings, input focus glow, card header/footer separators
- **CSS variables:** Unified design tokens for colors, spacing, typography

### v2.0.0 (2026-05-02)
- **Data layer:** JSON files → SQLite + SQLAlchemy 2.0 (async)
- **Migration guide:** 70 Azure services with cross-subscription move intelligence
- **Search integration:** Pricing results include migration warnings
- **Caching:** cachetools TTLCache for pricing/updates/health
- **Admin panel:** Web UI for user management (`/admin`)
- **Private mode:** Registration disabled; admin creates users via CLI or panel
- **Data migration:** `scripts/migrate_json_to_sqlite.py` for existing data
- Architecture: routes → services → models separation

### v1.0.0 — Initial release
- Multi-user JWT auth, pricing, docs, updates, reports, meetings, snippets, bookmarks

---

## 📝 License

MIT
