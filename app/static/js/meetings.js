// ASE Hub - Meetings

async function saveMeeting() {
    const title = document.getElementById('meeting-title').value.trim();
    const date = document.getElementById('meeting-date').value;
    const attendees = document.getElementById('meeting-attendees').value.trim();
    const notes = document.getElementById('meeting-notes').value.trim();
    const actionsRaw = document.getElementById('meeting-actions').value.trim();
    
    if (!title) {
        showToast('Please enter a meeting title', 'warning');
        return;
    }
    
    const actionItems = actionsRaw ? actionsRaw.split('\n').map(a => a.trim()).filter(a => a) : [];
    
    const data = await apiPost('/api/meetings', {
        title, date, attendees, notes, action_items: actionItems
    });
    
    if (data) {
        showToast('Meeting saved with AI summary!', 'success');
        document.getElementById('meeting-title').value = '';
        document.getElementById('meeting-attendees').value = '';
        document.getElementById('meeting-notes').value = '';
        document.getElementById('meeting-actions').value = '';
        loadMeetings();
    }
}

async function loadMeetings() {
    const el = document.getElementById('meetings-list');
    if (!el) return;
    setLoading('meetings-list');
    
    const data = await apiGet('/api/meetings');
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">' + t('no_meetings') + '</div>';
        return;
    }
    
    if (data.items.length === 0) {
        el.innerHTML = '<div class="empty-state">' + t('no_meetings') + '</div>';
        return;
    }
    
    let html = '';
    data.items.slice().reverse().forEach(m => {
        html += `<div class="report-card">
            <div class="project">${m.title || 'Untitled'}</div>
            <div class="date">${m.date || ''} — ${m.attendees || ''}</div>
            <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">${(m.summary || '').substring(0, 120)}</div>
            <button class="btn btn-sm" style="margin-top:4px" onclick="exportMeetingMd('${m.id}')">📥 ${t('export_md')}</button>
        </div>`;
    });
    el.innerHTML = html;
}

async function exportMeetingMd(id) {
    const data = await apiGet('/api/meetings/' + id + '/markdown');
    if (data && data.markdown) {
        document.getElementById('meeting-md-preview-card').style.display = 'block';
        document.getElementById('meeting-md-preview-content').textContent = data.markdown;
        document.getElementById('meeting-md-preview-card').scrollIntoView({ behavior: 'smooth' });
    }
}
