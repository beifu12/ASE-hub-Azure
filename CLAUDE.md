# ASE Hub - Azure Solutions Engineer Hub

A web dashboard for Azure solutions engineers: pricing queries, documentation search, Azure updates, work reports, and meeting summaries.

## Tech Stack
- Backend: Python 3 + FastAPI + httpx + feedparser
- Frontend: Single-page HTML/CSS/JS (vanilla, no framework)
- Container: Docker (python:3.12-slim base)
- APIs: Azure Retail Prices API, Azure REST API, RSS feeds

## Directory Structure
```
/root/projects/ase-hub/
  app/
    main.py              # FastAPI entry point
    routes/
      api.py             # REST endpoints
      pages.py           # HTML page routes
    services/
      pricing.py         # Azure Retail Prices API client
      docs.py            # Azure docs search
      updates.py         # RSS feeds (Azure Updates blog)
      health.py          # Azure Service Health
      reports.py         # Daily report generator
      meetings.py        # Meeting summary tool
      snippets.py        # CLI/ARM/Bicep snippets
    templates/
      index.html         # Main SPA dashboard
    static/
      css/
        style.css
      js/
        app.js
        dashboard.js
        pricing.js
        docs.js
        reports.js
        meetings.js
  requirements.txt
  Dockerfile
```

## Features

### 1. Dashboard (Homepage)
- Live Azure status badges (service health from Azure status RSS)
- Recent Azure feature updates (from Azure Updates RSS feed)
- Quick links / bookmarks
- Search bar (searches across all modules)

### 2. Pricing Query
- Search Azure services by name/keyword
- Call Azure Retail Prices API: https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines'
- Display: service name, region, unit price, meter
- Filter by region dropdown
- Results table with sortable columns

### 3. Documentation Search
- Search box that queries Azure Docs
- Use Microsoft Learn API or scrape docs
- Show title, summary, link
- Bookmark/save articles

### 4. Azure Updates Feed
- Fetch from: https://azure.microsoft.com/en-us/updates/feed/ (RSS)
- Show latest 20 updates
- Filter by category (Compute, Networking, Storage, AI, etc.)
- Refresh button

### 5. Daily Work Report
- Form: date, project, tasks completed, blockers, next steps
- Save as local JSON file (persistent)
- List previous reports
- Export as Markdown

### 6. Meeting Summary
- Form: meeting title, date, attendees, notes, action items
- AI summary button (generate summary from notes)
- Save as local JSON
- Export as Markdown

### 7. Azure CLI Cheat Sheet (Bonus)
- Pre-loaded common commands by category
- Copy-to-clipboard buttons
- Searchable

### 8. Architecture Reference (Bonus)
- Common Azure architecture patterns
- Mermaid diagram rendering
- Link to Azure Architecture Center

## UX Requirements
- Dark theme (Azure Portal style)
- Responsive (mobile + desktop)
- Sidebar navigation
- Loading spinners
- Toast notifications for actions
- Chinese + English bilingual (language toggle)

## API Endpoints
- GET /api/pricing?keyword=VM&region=eastasia
- GET /api/docs?q=azure+functions
- GET /api/updates
- GET /api/health
- POST /api/reports
- GET /api/reports
- POST /api/meetings
- GET /api/meetings
- GET /api/snippets?category=compute
- GET /api/bookmarks
- POST /api/bookmarks

## Docker
- Expose port 8000
- Health check on /api/health
- Data persistence: mount /app/data for reports/meetings JSON files
