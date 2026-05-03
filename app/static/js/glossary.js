// ASE Hub — Azure Glossary (v3 simplified)
// Core: translate + pronounce + history (50) + favorites
// No hot words, no category browser, no service grid

let _debounceTimer = null;
let _recentSearches = [];
let _favorites = [];
let _lastResult = null;
const MAX_HISTORY = 50;
const STORAGE_KEY_HISTORY = 'ase_glossary_history';
const STORAGE_KEY_FAVORITES = 'ase_glossary_favorites';

// ═══════════ Init ═══════════

function initGlossary() {
    try { _recentSearches = JSON.parse(localStorage.getItem(STORAGE_KEY_HISTORY) || '[]'); } catch (e) { _recentSearches = []; }
    try { _favorites = JSON.parse(localStorage.getItem(STORAGE_KEY_FAVORITES) || '[]'); } catch (e) { _favorites = []; }
    loadVoices();
    renderHistory();
}

// ═══════════ Search with suggestions ═══════════

function onGlossaryInput() {
    clearTimeout(_debounceTimer);
    const q = document.getElementById('glossary-input').value.trim();
    if (!q || q.length < 2) {
        document.getElementById('suggestions-dropdown').style.display = 'none';
        return;
    }
    _debounceTimer = setTimeout(() => fetchSuggestions(q), 250);
}

async function fetchSuggestions(q) {
    const data = await apiGet('/api/translate?q=' + encodeURIComponent(q));
    const dd = document.getElementById('suggestions-dropdown');
    if (!dd) return;

    if (data && data.found) {
        // Show single result + suggestion list
        showResult(data);
        dd.style.display = 'none';
        addToHistory(data.query, data.cn);
        return;
    }

    if (data && data.suggestions && data.suggestions.length > 0) {
        let html = '';
        data.suggestions.forEach(s => {
            html += `<div class="sug-row" onclick="selectSuggestion('${s.term.replace(/'/g, "\\'")}')">
                <span class="sug-term">${s.term}</span>
                <span class="sug-arrow">→</span>
                <span class="sug-cn">${s.cn}</span>
            </div>`;
        });
        dd.innerHTML = html;
        dd.style.display = 'block';
    } else {
        dd.innerHTML = '<div class="sug-row no-match">No matches in glossary</div>';
        dd.style.display = 'block';
    }
}

async function selectSuggestion(term) {
    document.getElementById('glossary-input').value = term;
    document.getElementById('suggestions-dropdown').style.display = 'none';
    const data = await apiGet('/api/translate?q=' + encodeURIComponent(term));
    if (data && data.found) {
        showResult(data);
        addToHistory(data.query, data.cn);
    }
}

function onGlossaryEnter(e) {
    if (e.key !== 'Enter') return;
    document.getElementById('suggestions-dropdown').style.display = 'none';
    const q = document.getElementById('glossary-input').value.trim();
    if (!q) return;
    doDirectSearch(q);
}

async function doDirectSearch(q) {
    const data = await apiGet('/api/translate?q=' + encodeURIComponent(q));
    if (data && data.found) {
        showResult(data);
        addToHistory(data.query, data.cn);
    } else if (data && data.suggestions && data.suggestions.length > 0) {
        // Pick first suggestion
        const first = data.suggestions[0];
        document.getElementById('glossary-input').value = first.term;
        const d2 = await apiGet('/api/translate?q=' + encodeURIComponent(first.term));
        if (d2 && d2.found) { showResult(d2); addToHistory(d2.query, d2.cn); }
    } else {
        document.getElementById('glossary-result').innerHTML = '<div class="empty-state">Not found in glossary</div>';
    }
}

// ═══════════ Result display ═══════════

function showResult(data) {
    _lastResult = data;
    const el = document.getElementById('glossary-result');
    const isFav = _favorites.includes(data.query);
    const phonetic = data.phonetic ? `<div class="gr-phonetic">${data.phonetic}</div>` : '';
    const scene = data.scene ? `<div class="gr-scene">📂 ${data.scene}</div>` : '';

    el.innerHTML = `
        <div class="gr-result-card">
            <div class="gr-term-row">
                <span class="gr-en">${data.query}</span>
                <div class="gr-speak-btns">
                    <button class="btn btn-sm" onclick="speakText('${data.query.replace(/'/g, "\\'")}', 'en-US-JennyNeural', this)" title="US pronunciation">🔊 US</button>
                    <button class="btn btn-sm" onclick="speakText('${data.query.replace(/'/g, "\\'")}', 'en-GB-SoniaNeural', this)" title="UK pronunciation">🔊 UK</button>
                </div>
            </div>
            ${phonetic}
            <div class="gr-cn">${data.cn}</div>
            ${scene}
            <div class="gr-actions">
                <button class="btn btn-sm ${isFav ? 'btn-warning' : ''}" onclick="toggleFavorite('${data.query.replace(/'/g, "\\'")}', this)" id="fav-btn">
                    ${isFav ? '⭐' : '☆'} ${isFav ? 'Favorited' : 'Favorite'}
                </button>
                <button class="btn btn-sm" onclick="copyToClipboard('${data.cn.replace(/'/g, "\\'")}', this)">📋 Copy</button>
                <button class="btn btn-sm btn-primary" onclick="openGlossaryBlade('${data.query.replace(/'/g, "\\'")}')">ℹ️ Details</button>
            </div>
        </div>`;
}

// ═══════════ History (50 recent) ═══════════

function addToHistory(term, cn) {
    _recentSearches = _recentSearches.filter(h => h.term !== term);
    _recentSearches.unshift({ term, cn, time: Date.now() });
    if (_recentSearches.length > MAX_HISTORY) _recentSearches = _recentSearches.slice(0, MAX_HISTORY);
    localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(_recentSearches));
    renderHistory();
}

function renderHistory() {
    const el = document.getElementById('glossary-history');
    if (!el) return;
    if (_recentSearches.length === 0) {
        el.innerHTML = '<div class="empty-state">Search history will appear here</div>';
        return;
    }
    let html = '<div class="gh-header">Recent searches (' + _recentSearches.length + ')</div>';
    _recentSearches.forEach((h, i) => {
        const isFav = _favorites.includes(h.term);
        html += `<div class="gh-row" onclick="reSearch('${h.term.replace(/'/g, "\\'")}')">
            <button class="btn btn-sm" onclick="event.stopPropagation(); speakText('${h.term.replace(/'/g, "\\'")}', 'en-US-JennyNeural', this)">🔊</button>
            <span class="gh-term">${h.term}</span>
            <span class="gh-arrow">→</span>
            <span class="gh-cn">${h.cn || '...'}</span>
            <span class="gh-fav ${isFav ? 'active' : ''}" onclick="event.stopPropagation(); toggleFavorite('${h.term.replace(/'/g, "\\'")}')">${isFav ? '⭐' : '☆'}</span>
        </div>`;
    });
    el.innerHTML = html;
}

async function reSearch(term) {
    document.getElementById('glossary-input').value = term;
    const data = await apiGet('/api/translate?q=' + encodeURIComponent(term));
    if (data && data.found) {
        showResult(data);
        addToHistory(data.query, data.cn);
    }
    document.getElementById('section-glossary').scrollIntoView({ behavior: 'smooth' });
}

// ═══════════ Favorites ═══════════

function toggleFavorite(term, btn) {
    const idx = _favorites.indexOf(term);
    if (idx >= 0) {
        _favorites.splice(idx, 1);
        if (btn) { btn.innerHTML = '☆ Favorite'; btn.classList.remove('btn-warning'); }
    } else {
        _favorites.push(term);
        if (btn) { btn.innerHTML = '⭐ Favorited'; btn.classList.add('btn-warning'); }
    }
    localStorage.setItem(STORAGE_KEY_FAVORITES, JSON.stringify(_favorites));
    renderHistory();
    // Update result card fav button if visible
    const fb = document.getElementById('fav-btn');
    if (fb) {
        const isFav = _favorites.includes(term);
        fb.innerHTML = (isFav ? '⭐' : '☆') + ' ' + (isFav ? 'Favorited' : 'Favorite');
        if (isFav) fb.classList.add('btn-warning'); else fb.classList.remove('btn-warning');
    }
}

// ═══════════ Copy ═══════════

function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        if (btn) { const orig = btn.textContent; btn.textContent = '✅ Copied!'; setTimeout(() => btn.textContent = orig, 1500); }
    });
}

// ═══════════ TTS (shared with old code) ═══════════

let currentAudio = null;

async function speakText(text, voice, btn) {
    if (!text) return;
    if (btn) { btn.textContent = '⏳...'; btn.disabled = true; }
    const data = await apiPost('/api/tts', { text, voice: voice || 'en-US-JennyNeural' });
    if (!data || data.error) {
        if (btn) { btn.textContent = '🔊'; btn.disabled = false; }
        return;
    }
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    const audio = new Audio(data.url);
    currentAudio = audio;
    audio.onended = () => { if (btn) { btn.textContent = '🔊'; btn.disabled = false; } };
    audio.onerror = () => { if (btn) { btn.textContent = '🔊'; btn.disabled = false; } };
    audio.play();
}

async function loadVoices() {} // No-op: voice is hardcoded per button

// ═══════════ Blade detail ═══════════

function openGlossaryBlade(term) {
    let data = null;
    if (_lastResult && _lastResult.query === term) {
        data = _lastResult;
    } else {
        data = _recentSearches.find(h => h.term === term);
    }
    if (!data) return;
    const phonetic = data.phonetic ? `<div class="blade-detail__phonetic">${data.phonetic}</div>` : '';
    const scene = data.scene ? `<div class="blade-detail__scene">${data.scene}</div>` : '';
    const desc = data.desc ? `<div class="blade-detail__desc">${data.desc}</div>` : '';
    const html = `
        <div class="blade-detail">
            <div class="blade-detail__term">${data.query || data.term}</div>
            ${phonetic}
            <div class="blade-detail__cn">${data.cn || ''}</div>
            ${scene}
            ${desc}
        </div>`;
    openBlade(data.query || data.term, html);
}

// Hide suggestions on outside click
document.addEventListener('click', (e) => {
    if (!e.target.closest('#glossary-input') && !e.target.closest('#suggestions-dropdown')) {
        const dd = document.getElementById('suggestions-dropdown');
        if (dd) dd.style.display = 'none';
    }
});

// Init
document.addEventListener('DOMContentLoaded', initGlossary);
