// ASE Hub - Dashboard

async function loadDashboard() {
    loadStatus();
    loadUpdatesSummary();
    loadBookmarks();
    updateStats();
}

async function loadStatus() {
    const el = document.getElementById('status-list');
    if (!el) return;
    setLoading('status-list');
    const data = await apiGet('/api/status');
    if (!data || !data.services) {
        el.innerHTML = '<div class="empty-state">Unable to load status</div>';
        return;
    }
    let html = '';
    data.services.slice(0, 8).forEach(s => {
        const title = s.title || 'Unknown';
        const isGood = title.toLowerCase().includes('good') || title.toLowerCase().includes('normal');
        const isWarning = title.toLowerCase().includes('warning') || title.toLowerCase().includes('degraded');
        const dotClass = isGood ? 'green' : (isWarning ? 'yellow' : 'green');
        html += `<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:13px">
            <span class="status-dot ${dotClass}"></span>${title}
        </div>`;
    });
    el.innerHTML = html || '<div class="empty-state">No status data</div>';
    document.getElementById('stat-status').textContent = data.services.length > 0 ? '🟢 OK' : '⚠️';
}

async function loadUpdatesSummary() {
    const el = document.getElementById('updates-summary');
    if (!el) return;
    setLoading('updates-summary');
    const data = await apiGet('/api/updates?category=');
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">Unable to load updates</div>';
        return;
    }
    let html = '';
    data.items.slice(0, 8).forEach(u => {
        html += `<div style="padding:8px 0;border-bottom:1px solid var(--border)">
            <a href="${u.link || '#'}" target="_blank" rel="noopener" style="color:var(--accent-light);text-decoration:none;font-size:13px">${u.title || 'Untitled'}</a>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">${u.published || ''}</div>
        </div>`;
    });
    el.innerHTML = html || '<div class="empty-state">No updates</div>';
    document.getElementById('stat-updates').textContent = data.count;
}

async function loadBookmarks() {
    const el = document.getElementById('bookmarks-list');
    if (!el) return;
    setLoading('bookmarks-list');
    const data = await apiGet('/api/bookmarks');
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">No bookmarks</div>';
        return;
    }
    let html = '';
    data.items.forEach(b => {
        html += `<div class="bookmark-item">
            <div>
                <a href="${b.url || '#'}" target="_blank" rel="noopener">${b.title || 'Untitled'}</a>
                <div style="font-size:11px;color:var(--text-secondary)">${b.description || ''}</div>
            </div>
        </div>`;
    });
    el.innerHTML = html || '<div class="empty-state">No bookmarks saved</div>';
    document.getElementById('stat-bookmarks').textContent = data.count;
}

async function updateStats() {
    try {
        const [statusData, updatesData, bmData] = await Promise.all([
            apiGet('/api/status'),
            apiGet('/api/updates?category='),
            apiGet('/api/bookmarks')
        ]);
        if (statusData) document.getElementById('stat-status').textContent = statusData.services && statusData.services.length > 0 ? '🟢 OK' : '⚠️';
        if (updatesData) document.getElementById('stat-updates').textContent = updatesData.count || 0;
        if (bmData) document.getElementById('stat-bookmarks').textContent = bmData.count || 0;
    } catch(e) {}
}
