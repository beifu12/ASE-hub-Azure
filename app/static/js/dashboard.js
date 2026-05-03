// ASE Hub - Dashboard

async function loadDashboard() {
    loadStatus();
    loadVMStatus();
    loadUserInfo();
    loadUpdatesSummary();
    loadBookmarks();
}

async function loadStatus() {
    const el = document.getElementById('tile-body-status');
    if (!el) return;
    setLoading('tile-body-status');
    const data = await apiGet('/api/status');
    if (!data || !data.services) {
        el.innerHTML = '<div class="tile__meta">Unable to load status</div>';
        const tile = document.getElementById('tile-status');
        if (tile) { tile.classList.remove('tile--ok'); tile.classList.add('tile--error'); }
        return;
    }
    const isGood = data.services.length > 0 && data.services.some(s => {
        const title = (s.title || '').toLowerCase();
        return title.includes('good') || title.includes('normal');
    });
    const statusText = isGood ? '🟢 Normal' : '⚠️ Warning';
    el.innerHTML = '<div class="tile__value">' + statusText + '</div><div class="tile__meta">' + (data.services.length || 0) + ' services monitored</div>';
    const tile = document.getElementById('tile-status');
    if (tile) {
        tile.classList.remove('tile--ok', 'tile--warning', 'tile--error');
        tile.classList.add(isGood ? 'tile--ok' : 'tile--warning');
    }

    // Also update health tile if present
    const healthEl = document.getElementById('tile-body-health');
    if (healthEl) {
        let html = '';
        data.services.slice(0, 5).forEach(s => {
            const title = s.title || 'Unknown';
            const t = title.toLowerCase();
            const isGood = t.includes('good') || t.includes('normal');
            const isWarning = t.includes('warning') || t.includes('degraded');
            const dotClass = isGood ? 'green' : (isWarning ? 'yellow' : 'green');
            html += '<div class="tile__list-item"><span class="status-dot ' + dotClass + '"></span>' + title + '</div>';
        });
        healthEl.innerHTML = html || '<div class="tile__meta">No status data</div>';
        const healthTile = document.getElementById('tile-health');
        if (healthTile) {
            healthTile.classList.remove('tile--ok', 'tile--warning', 'tile--error');
            healthTile.classList.add(isGood ? 'tile--ok' : 'tile--warning');
        }
    }
}

async function loadVMStatus() {
    const el = document.getElementById('tile-body-vm');
    if (!el) return;
    setLoading('tile-body-vm');
    const data = await apiGet('/api/health');
    if (!data) {
        el.innerHTML = '<div class="tile__meta">Unable to load VM status</div>';
        const tile = document.getElementById('tile-vm');
        if (tile) { tile.classList.remove('tile--ok'); tile.classList.add('tile--error'); }
        return;
    }
    const status = data.status || 'Unknown';
    const isHealthy = status.toLowerCase() === 'healthy' || status.toLowerCase() === 'ok';
    const display = isHealthy ? '🟢 Healthy' : '⚠️ ' + status;
    el.innerHTML = '<div class="tile__value">' + display + '</div><div class="tile__meta">Azure Health API</div>';
    const tile = document.getElementById('tile-vm');
    if (tile) {
        tile.classList.remove('tile--ok', 'tile--warning', 'tile--error');
        tile.classList.add(isHealthy ? 'tile--ok' : 'tile--warning');
    }
}

async function loadUserInfo() {
    const el = document.getElementById('tile-body-user');
    if (!el) return;
    const user = JSON.parse(localStorage.getItem('ase_user') || '{}');
    const name = user.display_name || user.username || 'Guest';
    const role = user.role || 'ASE';
    el.innerHTML = '<div class="tile__value">' + name + '</div><div class="tile__meta">' + role + '</div>';
}

async function loadUpdatesSummary() {
    const el = document.getElementById('tile-body-updates');
    if (!el) return;
    setLoading('tile-body-updates');
    const data = await apiGet('/api/updates?category=');
    if (!data || !data.items) {
        el.innerHTML = '<div class="tile__meta">Unable to load updates</div>';
        return;
    }
    let html = '';
    data.items.slice(0, 5).forEach(u => {
        html += '<div class="tile__list-item">' +
            '<a href="' + (u.link || '#') + '" target="_blank" rel="noopener">' + (u.title || 'Untitled') + '</a>' +
            '<span style="margin-left:auto;font-size:11px;color:var(--text-secondary);white-space:nowrap">' + (u.published || '') + '</span>' +
            '</div>';
    });
    el.innerHTML = html || '<div class="tile__meta">No updates</div>';
}

async function loadBookmarks() {
    const el = document.getElementById('tile-body-bookmarks');
    if (!el) return;
    setLoading('tile-body-bookmarks');
    const data = await apiGet('/api/bookmarks');
    if (!data || !data.items) {
        el.innerHTML = '<div class="tile__meta">No bookmarks</div>';
        return;
    }
    let html = '';
    data.items.forEach(b => {
        html += '<div class="tile__list-item">' +
            '<a href="' + (b.url || '#') + '" target="_blank" rel="noopener">' + (b.title || 'Untitled') + '</a>' +
            '</div>';
    });
    el.innerHTML = html || '<div class="tile__meta">No bookmarks saved</div>';
}
