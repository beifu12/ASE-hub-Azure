// ASE Hub - Navigation & Sidebar

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main-content');
    sidebar.classList.toggle('sidebar--collapsed');
    main.classList.toggle('main-content--expanded');
    localStorage.setItem('sidebar-collapsed',
        sidebar.classList.contains('sidebar--collapsed'));
}

function toggleGroup(groupId) {
    const nav = document.getElementById('group-' + groupId);
    if (!nav) return;
    const chevron = nav.previousElementSibling.querySelector('.sidebar__chevron');
    nav.classList.toggle('sidebar__nav--collapsed');
    if (chevron) {
        chevron.textContent = nav.classList.contains('sidebar__nav--collapsed') ? '▸' : '▾';
    }
}

function trackRecent(section) {
    let recent = JSON.parse(localStorage.getItem('recent-sections') || '[]');
    recent = [section, ...recent.filter(s => s !== section)].slice(0, 5);
    localStorage.setItem('recent-sections', JSON.stringify(recent));
    renderRecentNav();
}

function renderRecentNav() {
    const nav = document.getElementById('recent-nav');
    if (!nav) return;
    const recent = JSON.parse(localStorage.getItem('recent-sections') || '[]');
    const sectionMeta = {
        dashboard:  { icon: '📊', i18n: 'dashboard' },
        pricing:    { icon: '💰', i18n: 'pricing' },
        docs:       { icon: '📚', i18n: 'docs' },
        updates:    { icon: '📡', i18n: 'updates' },
        reports:    { icon: '📝', i18n: 'reports' },
        meetings:   { icon: '🤝', i18n: 'meetings' },
        glossary:   { icon: '📖', i18n: 'glossary' },
        snippets:   { icon: '⚡', i18n: 'snippets' },
        migration:  { icon: '🔄', i18n: 'migration' },
    };
    if (!recent.length) {
        nav.innerHTML = '<div class="nav-item" style="cursor:default;opacity:0.4"><span class="icon">—</span> <span>No recent</span></div>';
        return;
    }
    nav.innerHTML = recent.map(s => {
        const meta = sectionMeta[s] || { icon: '•', i18n: s };
        return '<a class="nav-item" data-section="' + s + '" onclick="navigateTo(\'' + s + '\')">' +
            '<span class="icon">' + meta.icon + '</span> <span data-i18n="' + meta.i18n + '">' + s + '</span>' +
            '</a>';
    }).join('');
}

const BREADCRUMB_MAP = {
    dashboard:  ['dashboard'],
    pricing:    ['group_knowledge', 'pricing'],
    docs:       ['group_knowledge', 'docs'],
    updates:    ['group_tools', 'updates'],
    reports:    ['group_workspace', 'reports'],
    meetings:   ['group_workspace', 'meetings'],
    glossary:   ['group_knowledge', 'glossary'],
    snippets:   ['group_admin', 'snippets'],
    migration:  ['group_admin', 'migration'],
};

function updateBreadcrumb(section) {
    const bc = document.getElementById('breadcrumb');
    if (!bc) return;
    const keys = BREADCRUMB_MAP[section] || [section];
    const labels = keys.map((k, i) => {
        const isLast = i === keys.length - 1;
        const label = t(k);
        return isLast
            ? '<span class="breadcrumb__item breadcrumb__item--active">' + label + '</span>'
            : '<span class="breadcrumb__item">' + label + '</span>';
    });
    const seps = keys.slice(1).map(() => '<span class="breadcrumb__sep">›</span>');
    let html = '';
    for (let i = 0; i < labels.length; i++) {
        html += labels[i];
        if (i < seps.length) html += seps[i];
    }
    bc.innerHTML = html;
}

function navigateTo(section) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.nav-item[data-section="' + section + '"]').forEach(b => b.classList.add('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const target = document.getElementById('section-' + section);
    if (target) {
        target.classList.add('active');
        if (section === 'dashboard') { loadDashboard(); }
        if (section === 'updates') { loadUpdates(); }
        if (section === 'snippets') { loadSnippets(); }
        if (section === 'reports') { loadReports(); }
        if (section === 'meetings') { loadMeetings(); }
        if (section === 'migration') { loadMigrationStats(); }
    }
    updateBreadcrumb(section);
    trackRecent(section);
    if (window.innerWidth < 768) {
        document.querySelector('.sidebar').classList.remove('open');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        toggleSidebar();
    }
    renderRecentNav();
    updateBreadcrumb('dashboard');
});
