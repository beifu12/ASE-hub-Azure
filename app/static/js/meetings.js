// ASE Hub - Meetings

async function saveMeeting() {
    const editingId = document.getElementById('editing-meeting-id')?.value;
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
    
    let data;
    if (editingId) {
        data = await apiPut('/api/meetings/' + editingId, {
            title, date, attendees, notes, action_items: actionItems
        });
    } else {
        data = await apiPost('/api/meetings', {
            title, date, attendees, notes, action_items: actionItems
        });
    }
    
    if (data && !data.error) {
        showToast(editingId ? 'Meeting updated!' : 'Meeting saved with AI summary!', 'success');
        document.getElementById('meeting-title').value = '';
        document.getElementById('meeting-attendees').value = '';
        document.getElementById('meeting-notes').value = '';
        document.getElementById('meeting-actions').value = '';
        if (document.getElementById('editing-meeting-id')) {
            document.getElementById('editing-meeting-id').value = '';
        }
        document.getElementById('meeting-submit-btn').textContent = '💾 Save Meeting';
        loadMeetings();
    } else if (data && data.error) {
        showToast(data.error, 'warning');
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
        html += `<div class="report-card" id="meeting-${m.id}">
            <div class="project">${m.title || 'Untitled'}</div>
            <div class="date">${m.date || ''} — ${m.attendees || ''}</div>
            <div style="margin-top:4px;font-size:12px;color:var(--text-secondary)">${(m.notes || m.summary || '').substring(0, 120)}</div>
            <div style="margin-top:6px;display:flex;gap:4px">
                <button class="btn btn-sm" onclick="exportMeetingMd('${m.id}')">📥 ${t('export_md')}</button>
                <button class="btn btn-sm" onclick="editMeeting('${m.id}')">✏️ ${t('edit') || 'Edit'}</button>
                <button class="btn btn-sm btn-danger" onclick="deleteMeeting('${m.id}')">🗑️ ${t('delete') || 'Delete'}</button>
            </div>
        </div>`;
    });
    el.innerHTML = html;
}

async function editMeeting(id) {
    const card = document.getElementById('meeting-' + id);
    if (!card) return;
    const titleEl = card.querySelector('.project');
    const dateEl = card.querySelector('.date');
    if (!titleEl || !dateEl) return;
    const title = titleEl.textContent || '';
    const date = dateEl.textContent.split(' — ')[0] || '';
    document.getElementById('meeting-title').value = title;
    document.getElementById('meeting-date').value = date;
    document.getElementById('meeting-attendees').value = '';
    document.getElementById('meeting-notes').value = '';
    document.getElementById('meeting-actions').value = '';
    document.getElementById('editing-meeting-id').value = id;
    document.getElementById('meeting-submit-btn').textContent = '✏️ Update Meeting';
    document.getElementById('section-meetings').scrollIntoView({ behavior: 'smooth' });
    showToast('Editing meeting — modify and click Update', 'info');
}

async function deleteMeeting(id) {
    if (!confirm('Delete this meeting? This cannot be undone.')) return;
    const data = await apiDelete('/api/meetings/' + id);
    if (data && data.deleted) {
        showToast('Meeting deleted', 'success');
        loadMeetings();
    }
}

async function exportMeetingMd(id) {
    const data = await apiGet('/api/meetings/' + id + '/markdown');
    if (data && data.markdown) {
        document.getElementById('meeting-md-preview-card').style.display = 'block';
        document.getElementById('meeting-md-preview-content').textContent = data.markdown;
        document.getElementById('meeting-md-preview-card').scrollIntoView({ behavior: 'smooth' });
    }
}
