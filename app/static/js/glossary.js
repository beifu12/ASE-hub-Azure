// ASE Hub — Azure Glossary & TTS

let currentVoice = 'en-US-JennyNeural';
let currentAudio = null;

// ═══════════ TRANSLATE ═══════════

async function doTranslate() {
    const input = document.getElementById('glossary-input');
    const result = document.getElementById('translate-result');
    const q = input.value.trim();
    if (!q) return;

    result.innerHTML = '<div class="loading">🔍 Searching glossary...</div>';

    const data = await apiGet('/api/translate?q=' + encodeURIComponent(q));
    if (!data) { result.innerHTML = '<div class="error">API error</div>'; return; }

    if (data.found) {
        const phonetic = data.phonetic ? `<span class="phonetic">${data.phonetic}</span>` : '';
        result.innerHTML = `
            <div class="translate-card found">
                <div class="tc-term">${data.query}</div>
                <div class="tc-cn">${data.cn}</div>
                ${phonetic}
                <div class="tc-scene">📂 ${data.scene}</div>
                <div class="tc-actions">
                    <button class="btn btn-primary btn-sm" onclick="speakText('${data.query.replace(/'/g, "\\'")}')">🔊 Pronounce</button>
                    <span class="tc-match-type">${data.match_type} match</span>
                </div>
            </div>`;
    } else if (data.suggestions && data.suggestions.length > 0) {
        let html = `<div class="translate-card not-found">
            <div class="tc-term">${data.query} <span class="tc-notfound">— not found</span></div>
            <div class="tc-hint">${data.hint}</div>
            <div class="suggestions">`;
        data.suggestions.forEach(s => {
            html += `<div class="sug-item" onclick="document.getElementById('glossary-input').value='${s.term}'; doTranslate();">
                <span class="sug-term">${s.term}</span>
                <span class="sug-cn">${s.cn}</span>
                <button class="btn btn-sm" onclick="event.stopPropagation(); speakText('${s.term.replace(/'/g, "\\'")}')">🔊</button>
            </div>`;
        });
        html += '</div></div>';
        result.innerHTML = html;
    } else {
        result.innerHTML = `<div class="translate-card not-found">
            <div class="tc-term">${data.query} <span class="tc-notfound">— not in glossary</span></div>
            <div class="tc-hint">${data.hint || 'Try a different term'}</div>
            <button class="btn btn-sm" style="margin-top:8px" onclick="speakText('${data.query.replace(/'/g, "\\'")}')">🔊 Pronounce anyway</button>
        </div>`;
    }
}

// ═══════════ TTS ═══════════

async function speakText(text) {
    if (!text) return;
    const btn = event?.target;
    if (btn) { btn.textContent = '⏳ Generating...'; btn.disabled = true; }

    const data = await apiPost('/api/tts', { text, voice: currentVoice });
    if (!data || data.error) {
        showToast(data?.error || 'TTS failed', 'error');
        if (btn) { btn.textContent = '🔊 Pronounce'; btn.disabled = false; }
        return;
    }

    // Play audio
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    const audio = new Audio(data.url);
    currentAudio = audio;
    audio.onended = () => { if (btn) { btn.textContent = '🔊 Pronounce'; btn.disabled = false; } };
    audio.onerror = () => { showToast('Audio playback failed', 'error'); if (btn) { btn.textContent = '🔊 Pronounce'; btn.disabled = false; } };
    audio.play();
    if (btn) { btn.textContent = '🔊 Playing...'; }
}

async function loadVoices() {
    const data = await apiGet('/api/tts/voices');
    if (!data || !data.voices) return;
    const sel = document.getElementById('tts-voice-select');
    if (!sel) return;
    sel.innerHTML = data.voices.map(v =>
        `<option value="${v.id}" ${v.id === currentVoice ? 'selected' : ''}>${v.name}</option>`
    ).join('');
}

function changeVoice() {
    currentVoice = document.getElementById('tts-voice-select')?.value || 'en-US-JennyNeural';
}

// ═══════════ GLOSSARY BROWSER ═══════════

async function loadGlossary() {
    const el = document.getElementById('glossary-list');
    if (!el) return;
    el.innerHTML = '<div class="loading">Loading glossary...</div>';

    const kw = document.getElementById('glossary-search')?.value || '';
    const data = await apiGet('/api/glossary?keyword=' + encodeURIComponent(kw) + '&limit=200');
    if (!data || !data.items) {
        el.innerHTML = '<div class="empty-state">No terms found</div>';
        return;
    }

    if (data.items.length === 0) {
        el.innerHTML = '<div class="empty-state">No matching terms</div>';
        return;
    }

    let html = `<div class="glossary-header">📖 ${data.items.length} of ${data.total} terms</div><div class="glossary-grid">`;
    data.items.forEach(item => {
        const phonetic = item.phonetic ? `<span class="phonetic-small">${item.phonetic}</span>` : '';
        html += `<div class="glossary-item">
            <div class="gi-term" onclick="document.getElementById('glossary-input').value='${item.term}'; doTranslate(); document.getElementById('section-glossary').scrollIntoView({behavior:'smooth'})">
                ${item.term}
            </div>
            <div class="gi-cn">${item.cn}</div>
            ${phonetic}
            <div class="gi-scene">${item.scene}</div>
            <button class="btn btn-sm" onclick="speakText('${item.term.replace(/'/g, "\\'")}')">🔊</button>
        </div>`;
    });
    html += '</div>';
    el.innerHTML = html;
}

async function loadCategories() {
    const data = await apiGet('/api/glossary/categories');
    if (!data || !data.categories) return;
    const el = document.getElementById('glossary-categories');
    if (!el) return;
    el.innerHTML = '<option value="">All Categories</option>' +
        data.categories.map(c => `<option value="${c}">${c}</option>`).join('');
}

function filterByCategory() {
    const cat = document.getElementById('glossary-categories')?.value || '';
    // Reload with category filter
    const el = document.getElementById('glossary-list');
    if (!el) return;
    el.innerHTML = '<div class="loading">Filtering...</div>';
    apiGet('/api/glossary?category=' + encodeURIComponent(cat) + '&limit=200').then(data => {
        if (!data || !data.items) { el.innerHTML = '<div class="empty-state">No terms</div>'; return; }
        let html = `<div class="glossary-header">📖 ${data.items.length} terms in "${cat || 'all'}"</div><div class="glossary-grid">`;
        data.items.forEach(item => {
            html += `<div class="glossary-item">
                <div class="gi-term">${item.term}</div>
                <div class="gi-cn">${item.cn}</div>
                <div class="gi-scene">${item.scene}</div>
                <button class="btn btn-sm" onclick="speakText('${item.term.replace(/'/g, "\\'")}')">🔊</button>
            </div>`;
        });
        html += '</div>';
        el.innerHTML = html;
    });
}

// Init on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVoices();
    loadCategories();
    loadGlossary();
});

// Enter key in input
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement?.id === 'glossary-input') {
        doTranslate();
    }
});
