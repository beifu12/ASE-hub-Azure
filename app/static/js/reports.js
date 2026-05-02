// ASE Hub - Reports

async function saveReport() {
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
    
    const data = await apiPost('/api/reports', {
        date, project, tasks, blockers, next_steps: nextSteps
    });
    
    if (data) {
        showToast('Report saved!', 'success');
        document.getElementById('report-project').value = '';
        document.getElementById('report-tasks').value = '';
        document.getElementById('report-blockers').value = '';
        document.getElementById('report-next').value = '';
        loadReports();
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
        html += `<div class="report-card">
            <div class="project">${r.project || 'Untitled'}</div>
            <div class="date">${r.date || ''} — ${r.tasks ? r.tasks.length : 0} tasks</div>
            <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">${(r.tasks || []).join(', ').substring(0, 100)}</div>
            <button class="btn btn-sm" style="margin-top:4px" onclick="exportReportMd('${r.id}')">📥 ${t('export_md')}</button>
        </div>`;
    });
    el.innerHTML = html;
}

async function exportReportMd(id) {
    const data = await apiGet('/api/reports/' + id + '/markdown');
    if (data && data.markdown) {
        document.getElementById('md-preview-card').style.display = 'block';
        document.getElementById('md-preview-content').textContent = data.markdown;
        document.getElementById('md-preview-card').scrollIntoView({ behavior: 'smooth' });
    }
}
