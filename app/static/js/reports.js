// ASE Hub - Reports

async function saveReport() {
    const editingId = document.getElementById('editing-report-id')?.value;
    const date = document.getElementById('report-date').value;
    const project = document.getElementById('report-project').value.trim();
    const tasksRaw = document.getElementById('report-tasks').value.trim();
    const blockers = document.getElementById('report-blockers').value.trim();
    const nextSteps = document.getElementById('report-next').value.trim();
    
    if (!project) {
        showToast('Please enter a project name', 'warning');
        return;
    }
    
    const tasks = tasksRaw ? tasksRaw.split('\n').map(t => t.trim()).filter(t => t) : [];
    
    let data;
    if (editingId) {
        data = await apiPut('/api/reports/' + editingId, {
            date, project, tasks, blockers, next_steps: nextSteps
        });
    } else {
        data = await apiPost('/api/reports', {
            date, project, tasks, blockers, next_steps: nextSteps
        });
    }
    
    if (data && !data.error) {
        showToast(editingId ? 'Report updated!' : 'Report saved!', 'success');
        document.getElementById('report-project').value = '';
        document.getElementById('report-tasks').value = '';
        document.getElementById('report-blockers').value = '';
        document.getElementById('report-next').value = '';
        if (document.getElementById('editing-report-id')) {
            document.getElementById('editing-report-id').value = '';
        }
        document.getElementById('report-submit-btn').textContent = '💾 Save Report';
        loadReports();
    } else if (data && data.error) {
        showToast(data.error, 'warning');
    }
}

async function loadReports() {
    const el = document.getElementById('reports-list');
    if (!el) return;
    setLoading('reports-list');
    
    const data = await apiGet('/api/reports');
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">' + t('no_reports') + '</div>';
        return;
    }
    
    if (data.items.length === 0) {
        el.innerHTML = '<div class="empty-state">' + t('no_reports') + '</div>';
        return;
    }
    
    let html = '';
    data.items.slice().reverse().forEach(r => {
        const tasksPreview = (r.tasks || []).join(', ').substring(0, 100);
        html += `<div class="report-card" id="report-${r.id}">
            <div class="project">${r.project || 'Untitled'}</div>
            <div class="date">${r.date || ''} — ${r.tasks ? r.tasks.length : 0} tasks</div>
            <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">${tasksPreview}</div>
            <div style="margin-top:6px;display:flex;gap:4px">
                <button class="btn btn-sm" onclick="exportReportMd('${r.id}')">📥 ${t('export_md')}</button>
                <button class="btn btn-sm" onclick="editReport('${r.id}')">✏️ ${t('edit') || 'Edit'}</button>
                <button class="btn btn-sm btn-danger" onclick="deleteReport('${r.id}')">🗑️ ${t('delete') || 'Delete'}</button>
            </div>
        </div>`;
    });
    el.innerHTML = html;
}

async function editReport(id) {
    const card = document.getElementById('report-' + id);
    if (!card) return;
    const titleEl = card.querySelector('.project');
    const dateEl = card.querySelector('.date');
    const tasksEl = card.querySelector('div[style]');
    if (!titleEl || !dateEl) return;
    const project = titleEl.textContent || '';
    const date = dateEl.textContent.split(' — ')[0] || '';
    document.getElementById('report-project').value = project;
    document.getElementById('report-date').value = date;
    document.getElementById('report-tasks').value = '';
    document.getElementById('report-blockers').value = '';
    document.getElementById('report-next').value = '';
    document.getElementById('editing-report-id').value = id;
    document.getElementById('report-submit-btn').textContent = '✏️ Update Report';
    document.getElementById('section-reports').scrollIntoView({ behavior: 'smooth' });
    showToast('Editing report — modify and click Update', 'info');
}

async function deleteReport(id) {
    if (!confirm('Delete this report? This cannot be undone.')) return;
    const data = await apiDelete('/api/reports/' + id);
    if (data && data.deleted) {
        showToast('Report deleted', 'success');
        loadReports();
    }
}

async function exportReportMd(id) {
    const data = await apiGet('/api/reports/' + id + '/markdown');
    if (data && data.markdown) {
        document.getElementById('md-preview-card').style.display = 'block';
        document.getElementById('md-preview-content').textContent = data.markdown;
        document.getElementById('md-preview-card').scrollIntoView({ behavior: 'smooth' });
    }
}
