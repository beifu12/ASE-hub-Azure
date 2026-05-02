// ASE Hub - Pricing

async function searchPricing() {
    const keyword = document.getElementById('pricing-keyword').value.trim();
    const region = document.getElementById('pricing-region').value;
    const tbody = document.getElementById('pricing-results');
    const countEl = document.getElementById('pricing-count');
    
    if (!keyword) {
        showToast('Please enter a service name', 'warning');
        return;
    }
    
    tbody.innerHTML = '<tr><td colspan="6"><div class="loading"><div class="spinner"></div></div></td></tr>';
    
    let url = '/api/pricing?keyword=' + encodeURIComponent(keyword);
    if (region) url += '&region=' + encodeURIComponent(region);
    
    const data = await apiGet(url);
    if (!data) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Error loading data</td></tr>';
        return;
    }
    
    countEl.textContent = '(' + data.count + ' items)';
    
    if (!data.items || data.items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-secondary)">No results found</td></tr>';
        return;
    }
    
    let html = '';
    data.items.forEach(item => {
        html += `<tr>
            <td>${item.serviceName || ''}</td>
            <td>${(item.productName || '').substring(0, 50)}</td>
            <td>${(item.meterName || '').substring(0, 60)}</td>
            <td>${item.armRegionName || ''}</td>
            <td>${item.unitPrice} ${item.currencyCode || 'USD'}</td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

async function loadUpdates() {
    const category = document.getElementById('updates-category').value;
    const el = document.getElementById('updates-list');
    if (!el) return;
    setLoading('updates-list');
    
    let url = '/api/updates';
    if (category) url += '?category=' + encodeURIComponent(category);
    
    const data = await apiGet(url);
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">Unable to load updates</div>';
        return;
    }
    
    let html = '';
    data.items.forEach(u => {
        html += `<div class="card" style="padding:12px 16px">
            <div style="font-weight:600;font-size:14px">
                <a href="${u.link || '#'}" target="_blank" rel="noopener" style="color:var(--accent-light);text-decoration:none">${u.title || 'Untitled'}</a>
            </div>
            <div style="font-size:12px;color:var(--text-secondary);margin-top:4px">${u.published || ''}</div>
            <div style="font-size:13px;margin-top:6px;color:var(--text-secondary)">${(u.summary || '').substring(0, 250)}</div>
        </div>`;
    });
    el.innerHTML = html || '<div class="empty-state">No updates found</div>';
}

async function loadSnippets() {
    const category = document.getElementById('snippets-category').value;
    const el = document.getElementById('snippets-list');
    if (!el) return;
    setLoading('snippets-list');
    
    let url = '/api/snippets';
    if (category) url += '?category=' + encodeURIComponent(category);
    
    const data = await apiGet(url);
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">No snippets</div>';
        return;
    }
    
    // Store for filtering
    window._snippets = data.items;
    renderSnippets(data.items);
}

function renderSnippets(items) {
    const el = document.getElementById('snippets-list');
    if (!el) return;
    let html = '';
    let currentCat = '';
    items.forEach(s => {
        const cat = s.category || 'general';
        if (cat !== currentCat) {
            currentCat = cat;
            html += `<h3 style="margin:16px 0 8px;text-transform:capitalize;color:var(--accent-light);font-size:14px">${cat}</h3>`;
        }
        html += `<div class="code-block" style="margin-bottom:12px;position:relative">
            <button class="copy-btn" onclick="copyToClipboard(\`${s.command.replace(/`/g,'\\`').replace(/'/g,"\\'")}\`, this)">📋 ${t('copy')}</button>
            <code>${s.command}</code>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:6px">${s.description || ''}</div>
        </div>`;
    });
    el.innerHTML = html || '<div class="empty-state">No snippets found</div>';
}

function filterSnippets() {
    const q = document.getElementById('snippets-search').value.toLowerCase();
    if (!window._snippets) return;
    if (!q) {
        renderSnippets(window._snippets);
        return;
    }
    const filtered = window._snippets.filter(s => 
        (s.command || '').toLowerCase().includes(q) || 
        (s.description || '').toLowerCase().includes(q) ||
        (s.category || '').toLowerCase().includes(q)
    );
    renderSnippets(filtered);
}
