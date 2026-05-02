// ASE Hub - Documentation Search

async function searchDocs() {
    const q = document.getElementById('docs-query').value.trim();
    const el = document.getElementById('docs-results');
    
    if (!q) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    const data = await apiGet('/api/docs?q=' + encodeURIComponent(q));
    if (!data) {
        el.innerHTML = '<div class="empty-state">Error loading docs</div>';
        return;
    }
    
    if (!data.items || data.items.length === 0) {
        el.innerHTML = '<div class="empty-state">No results found for "' + q + '"</div>';
        return;
    }
    
    let html = '';
    data.items.forEach(doc => {
        html += `<div class="card" style="padding:14px 16px">
            <div style="font-weight:600;font-size:14px;margin-bottom:6px">
                <a href="${doc.url || '#'}" target="_blank" rel="noopener" style="color:var(--accent-light);text-decoration:none">${doc.title || 'Untitled'}</a>
            </div>
            <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px">${doc.description || ''}</div>
            <button class="btn btn-sm" onclick="saveBookmark('${(doc.title || '').replace(/'/g,"\\'")}', '${(doc.url || '').replace(/'/g,"\\'")}', '${(doc.description || '').replace(/'/g,"\\'")}')">🔖 ${t('save_bookmark')}</button>
        </div>`;
    });
    el.innerHTML = html;
}

async function saveBookmark(title, url, description) {
    const data = await apiPost('/api/bookmarks', { title, url, description });
    if (data) {
        showToast('Bookmark saved!', 'success');
        if (document.getElementById('section-dashboard').classList.contains('active')) {
            loadBookmarks();
        }
    }
}
