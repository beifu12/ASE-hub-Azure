# 🏗️ ASE Hub — Azure Solutions Engineer Hub

[![Deploy](https://img.shields.io/badge/deploy-ASE%20Hub-blue)](https://ase.hefuzh.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A self-hosted, multi-user dashboard for Azure Solutions Engineers — unified pricing lookup, documentation search, update feeds, work reports, meeting summaries, and CLI cheat sheets.

> **Live demo:** https://ase.hefuzh.com

![Dashboard](https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoft-azure&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)

---

## ✨ Features

| Module | Description |
|---|---|
| 📊 **Dashboard** | Azure service health status, latest updates, quick links |
| 💰 **Pricing** | Fuzzy search across Azure Retail Prices API (service/product/meter) |
| 📚 **Docs** | Search Microsoft Azure documentation |
| 📡 **Updates** | RSS feed from Azure updates, filterable by category |
| 📝 **Reports** | Daily work reports with Markdown export |
| 🤝 **Meetings** | Meeting summaries with action items & Markdown export |
| ⚡ **Snippets** | Azure CLI & Bicep cheat sheets (12+ built-in snippets) |
| 🔖 **Bookmarks** | Save useful Azure links |

### 🔐 Multi-User Authentication

- JWT-based login/registration
- Per-user data isolation — each user sees only their own reports, meetings, bookmarks
- Token auto-refresh, logout, 401 auto-redirect
- User credentials stored locally (never committed to git)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development

```bash
# Clone
git clone https://github.com/beifu12/ASE-hub-Azure.git
cd ASE-hub-Azure

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 → register an account → done!

### Docker

```bash
# Build
docker build -t ase-hub .

# Run
docker run -d --name ase-hub -p 8000:8000 -v $(pwd)/data:/app/data ase-hub
```

### Azure Deployment

The project includes Terraform configs for Azure deployment:

```bash
cd terraform

# Initialize
terraform init

# Deploy (edit terraform.tfvars first)
terraform apply
```

This creates:
- Azure Container Registry (ACR)
- Virtual Network + Subnet
- Linux VM (Ubuntu 24.04) with Docker
- NSG with HTTP/SSH rules
- System-assigned managed identity with ACR pull role

---

## 📁 Project Structure

```
ase-hub/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── auth.py              # JWT auth, password hashing, middleware
│   ├── routes/
│   │   ├── api.py           # All API endpoints
│   │   └── pages.py         # Page routes (/, /login, /register)
│   ├── services/
│   │   ├── pricing.py       # Azure Retail Prices API client
│   │   ├── docs.py          # Azure documentation search
│   │   ├── updates.py       # Azure updates RSS feed
│   │   ├── health.py        # Azure service health
│   │   ├── reports.py       # Work reports CRUD
│   │   ├── meetings.py      # Meeting summaries CRUD
│   │   └── snippets.py      # CLI/Bicep cheat sheets
│   ├── templates/
│   │   ├── index.html       # Main dashboard
│   │   ├── login.html       # Login page
│   │   └── register.html    # Registration page
│   └── static/
│       ├── css/style.css    # Azure Portal dark theme
│       └── js/
│           ├── app.js       # Core app, I18N, auth, API wrapper
│           ├── dashboard.js  # Dashboard sections
│           ├── pricing.js    # Pricing search
│           ├── docs.js       # Docs search
│           ├── reports.js    # Reports CRUD
│           └── meetings.js   # Meetings CRUD
├── data/                    # Local storage (gitignored)
│   ├── users.json           # User accounts (bcrypt hashed)
│   ├── reports.json         # Work reports
│   ├── meetings.json        # Meeting summaries
│   └── .jwt_secret          # JWT signing key
├── terraform/               # Azure infrastructure as code
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
| GET | `/api/pricing?keyword=vm` | Azure pricing search |
| GET | `/api/docs?q=functions` | Azure docs search |
| GET | `/api/updates?category=compute` | Azure updates RSS |
| GET | `/api/status` | Azure service health |

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user info |

### Protected (requires `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports` | List user's reports |
| POST | `/api/reports` | Create report |
| GET | `/api/meetings` | List user's meetings |
| POST | `/api/meetings` | Create meeting |
| GET | `/api/snippets` | List snippets |
| GET | `/api/bookmarks` | List user's bookmarks |
| POST | `/api/bookmarks` | Create bookmark |

---

## 🛡️ Security

- Passwords hashed with **bcrypt**
- JWT tokens signed with auto-generated secret (stored in `data/.jwt_secret`)
- User data isolated — reports, meetings, bookmarks are per-user
- Frontend auto-redirects to login on 401
- `data/` directory excluded from git

---

## 🎨 Tech Stack

- **Backend:** FastAPI, Uvicorn, Python 3.12
- **Auth:** JWT (python-jose), bcrypt (passlib)
- **API Clients:** httpx, feedparser
- **Frontend:** Vanilla JS, CSS custom properties (Azure dark theme)
- **Infra:** Terraform, Docker, Azure VM + ACR
- **CDN/Proxy:** Cloudflare

---

## 📝 License

MIT
