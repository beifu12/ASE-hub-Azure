/* ═══════════════════════════════════════════════
   ASE Hub — WATS KB Search
   ═══════════════════════════════════════════════ */

let kbPageCurrent = 1;
let kbPageTotal = 1;
let kbQuery = '';

document.addEventListener('DOMContentLoaded', () => {
    loadKBFilters();
    loadKBStats();
});

async function loadKBFilters() {
    try {
        const res = await fetch('/api/kb/services');
        const data = await res.json();
        const domainSel = document.getElementById('kb-domain');
        const serviceSel = document.getElementById('kb-service');

        if (data.domains) {
            data.domains.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                domainSel.appendChild(opt);
            });
        }
        if (data.services) {
            data.services.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                serviceSel.appendChild(opt);
            });
        }
    } catch (e) {
        console.warn('Failed to load KB filters:', e);
    }
}

async function loadKBStats() {
    try {
        const res = await fetch('/api/kb/stats');
        const data = await res.json();
        const el = document.getElementById('kb-stats');
        if (el && data.total_entries) {
            el.textContent = `${data.total_entries} articles · ${data.services} services · ${data.domains} domains`;
        }
    } catch (e) {
        // ignore
    }
}

async function searchKB(page) {
    const q = document.getElementById('kb-query').value.trim();
    const domain = document.getElementById('kb-domain').value;
    const service = document.getElementById('kb-service').value;

    if (!q) {
        showToast('Please enter a search query', 'warning');
        return;
    }

    kbQuery = q;
    if (page) {
        kbPageCurrent = page;
    } else {
        kbPageCurrent = 1;
    }

    const container = document.getElementById('kb-results');
    container.innerHTML = '<div class="section-card"><div class="flex-center" style="justify-content:center;padding:40px"><div class="spinner"></div>&nbsp; Searching...</div></div>';

    try {
        const url = `/api/kb/search?q=${encodeURIComponent(q)}&domain=${encodeURIComponent(domain)}&service=${encodeURIComponent(service)}&page=${kbPageCurrent}&page_size=20`;
        const res = await fetch(url);
        const data = await res.json();

        if (!data.results || data.results.length === 0) {
            container.innerHTML = `<div class="section-card">
                <div class="empty-state">
                    <div class="empty-state__icon">🔍</div>
                    <div class="empty-state__title">No results found</div>
                    <div class="empty-state__desc">Try different keywords, or adjust the filters</div>
                </div>
            </div>`;
            document.getElementById('kb-pagination').style.display = 'none';
            return;
        }

        renderKBResults(data);
    } catch (e) {
        container.innerHTML = `<div class="section-card">
            <div class="empty-state">
                <div class="empty-state__icon">⚠️</div>
                <div class="empty-state__title">Search failed</div>
                <div class="empty-state__desc">${e.message}</div>
            </div>
        </div>`;
    }
}

function renderKBResults(data) {
    const container = document.getElementById('kb-results');
    kbPageTotal = data.total_pages || 1;

    let html = `<div class="section-card">
        <div class="kb-result-count">Found ${data.total} result(s) · Page ${data.page} of ${data.total_pages}</div>`;

    data.results.forEach(r => {
        const domainTag = r.domain ? `<span class="tag tag--blue">${r.domain}</span>` : '';
        const serviceTag = r.service ? `<span class="tag tag--green">${r.service}</span>` : '';
        const dateTag = r.modified ? `<span class="text-muted">${r.modified}</span>` : '';

        html += `<div class="search-result">
            <div class="search-result__title" onclick="openKBBlade('${r.id.replace(/'/g, "\\'")}')">${escapeHtml(r.title)}</div>
            <div class="search-result__meta">
                ${domainTag} ${serviceTag} ${dateTag}
            </div>
            <div class="search-result__summary">${r.summary || 'No summary available'}</div>
        </div>`;
    });

    // Save results data for blade
    window.__kbResults = data.results;

    html += '</div>';
    container.innerHTML = html;

    // Pagination
    const pag = document.getElementById('kb-pagination');
    if (data.total_pages > 1) {
        pag.style.display = 'flex';
        document.getElementById('kb-prev').disabled = kbPageCurrent <= 1;
        document.getElementById('kb-next').disabled = kbPageCurrent >= data.total_pages;
        document.getElementById('kb-page-info').textContent = `Page ${kbPageCurrent} of ${data.total_pages}`;
    } else {
        pag.style.display = 'none';
    }
}

function kbPage(dir) {
    const newPage = kbPageCurrent + dir;
    if (newPage < 1 || newPage > kbPageTotal) return;
    searchKB(newPage);
}

function openKBBlade(entryId) {
    const results = window.__kbResults || [];
    const entry = results.find(r => r.id === entryId);
    if (!entry) return;

    const body = document.getElementById('blade-body');
    const title = document.getElementById('blade-title');

    title.textContent = 'KB Article Details';

    body.innerHTML = `
        <div style="margin-bottom:16px">
            <div class="flex-wrap" style="display:flex;gap:8px;margin-bottom:8px">
                ${entry.domain ? `<span class="tag tag--blue">${escapeHtml(entry.domain)}</span>` : ''}
                ${entry.service ? `<span class="tag tag--green">${escapeHtml(entry.service)}</span>` : ''}
                ${entry.section ? `<span class="tag tag--yellow">${escapeHtml(entry.section)}</span>` : ''}
                ${entry.modified ? `<span class="text-muted" style="font-size:12px">${entry.modified}</span>` : ''}
            </div>
            <h2 style="font-size:18px;font-weight:600;margin-bottom:8px">${escapeHtml(entry.title)}</h2>
            <p style="color:var(--text-secondary);font-size:14px;line-height:1.6">${entry.summary.replace(/<\/?em>/g, '')}</p>
        </div>
        <div style="font-size:12px;color:var(--text-muted);padding-top:12px;border-top:1px solid var(--border-light)">
            Relevance score: ${entry.relevance || 'N/A'}
        </div>
    `;

    openBlade();
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
