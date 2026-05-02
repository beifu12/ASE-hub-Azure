// ASE Hub - Core App
const I18N = {
    en: {
        dashboard: "Dashboard",
        pricing: "Pricing",
        docs: "Docs",
        updates: "Updates",
        reports: "Reports",
        meetings: "Meetings",
        snippets: "Snippets",
        azure_status: "Azure Status",
        recent_updates: "Recent Updates",
        bookmarks: "Bookmarks",
        quick_links: "Quick Links",
        search: "Search",
        refresh: "Refresh",
        results: "Results",
        service: "Service",
        product: "Product",
        meter: "Meter",
        region: "Region",
        unit_price: "Unit Price",
        all_regions: "All Regions",
        all_categories: "All Categories",
        search_service: "Service name (e.g. Virtual Machines)",
        search_docs: "Search Azure documentation...",
        search_snippets: "Search snippets...",
        search_pricing_hint: "Enter a service name to search pricing",
        new_report: "New Report",
        saved_reports: "Saved Reports",
        save_report: "Save Report",
        no_reports: "No reports yet",
        markdown_export: "Markdown Export",
        new_meeting: "New Meeting",
        saved_meetings: "Saved Meetings",
        save_meeting: "Save Meeting",
        no_meetings: "No meetings yet",
        latest_updates: "Latest Azure Updates",
        date: "Date",
        project: "Project",
        tasks_completed: "Tasks completed (one per line)",
        blockers: "Blockers",
        next_steps: "Next steps",
        meeting_title: "Meeting title",
        attendees: "Attendees",
        meeting_notes: "Meeting notes (AI summary will be generated)",
        action_items: "Action items (one per line)",
        save_bookmark: "Save Bookmark",
        saved_bookmarks: "Saved Bookmarks",
        export_md: "Export Markdown",
        copy: "Copy",
        copied: "Copied!",
        loading: "Loading...",
    },
    zh: {
        dashboard: "仪表盘",
        pricing: "价格查询",
        docs: "文档搜索",
        updates: "Azure 更新",
        reports: "工作报告",
        meetings: "会议总结",
        snippets: "代码片段",
        azure_status: "Azure 状态",
        recent_updates: "最近更新",
        bookmarks: "书签",
        quick_links: "快速链接",
        search: "搜索",
        refresh: "刷新",
        results: "结果",
        service: "服务",
        product: "产品",
        meter: "计量",
        region: "区域",
        unit_price: "单价",
        all_regions: "所有区域",
        all_categories: "所有类别",
        search_service: "服务名称 (例如 Virtual Machines)",
        search_docs: "搜索 Azure 文档...",
        search_snippets: "搜索代码片段...",
        search_pricing_hint: "输入服务名称搜索价格",
        new_report: "新建报告",
        saved_reports: "已保存报告",
        save_report: "保存报告",
        no_reports: "暂无报告",
        markdown_export: "Markdown 导出",
        new_meeting: "新建会议",
        saved_meetings: "已保存会议",
        save_meeting: "保存会议",
        no_meetings: "暂无会议",
        latest_updates: "最新 Azure 更新",
        date: "日期",
        project: "项目",
        tasks_completed: "已完成任务 (每行一个)",
        blockers: "阻塞项",
        next_steps: "下一步",
        meeting_title: "会议标题",
        attendees: "参会人员",
        meeting_notes: "会议笔记 (将自动生成摘要)",
        action_items: "行动事项 (每行一个)",
        save_bookmark: "保存书签",
        saved_bookmarks: "已保存书签",
        export_md: "导出 Markdown",
        copy: "复制",
        copied: "已复制!",
        loading: "加载中...",
    }
};

let currentLang = 'en';

function t(key) {
    return (I18N[currentLang] && I18N[currentLang][key]) || (I18N['en'][key]) || key;
}

function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const section = btn.getAttribute('data-section');
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            const target = document.getElementById('section-' + section);
            if (target) {
                target.classList.add('active');
                // Load section data
                if (section === 'dashboard') { loadDashboard(); }
                if (section === 'updates') { loadUpdates(); }
                if (section === 'snippets') { loadSnippets(); }
                if (section === 'reports') { loadReports(); }
                if (section === 'meetings') { loadMeetings(); }
            }
            // Close sidebar on mobile
            if (window.innerWidth < 768) {
                document.querySelector('.sidebar').classList.remove('open');
            }
        });
    });

    // Language toggle
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLang = btn.getAttribute('data-lang');
            applyI18n();
        });
    });

    // Initialize
    initUserInfo();
    loadDashboard();

    // Set default date for forms
    const today = new Date().toISOString().split('T')[0];
    const reportDate = document.getElementById('report-date');
    const meetingDate = document.getElementById('meeting-date');
    if (reportDate) reportDate.value = today;
    if (meetingDate) meetingDate.value = today;
});

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Loading helper
function setLoading(elementId) {
    document.getElementById(elementId).innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

// Copy to clipboard
function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const origText = btn.textContent;
        btn.textContent = '✓ ' + t('copied');
        setTimeout(() => { btn.textContent = origText; }, 1500);
    }).catch(() => showToast('Copy failed', 'error'));
}

// Fetch wrapper with auth
function getAuthHeaders() {
    const token = localStorage.getItem('ase_token');
    if (token) return { 'Authorization': 'Bearer ' + token };
    return {};
}

async function apiGet(path) {
    try {
        const res = await fetch(path, { headers: getAuthHeaders() });
        if (res.status === 401) { handleUnauthorized(); return null; }
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (e) {
        showToast('API error: ' + e.message, 'error');
        return null;
    }
}

async function apiPost(path, data) {
    try {
        const res = await fetch(path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(data)
        });
        if (res.status === 401) { handleUnauthorized(); return null; }
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (e) {
        showToast('API error: ' + e.message, 'error');
        return null;
    }
}

// Auth helpers
function handleUnauthorized() {
    localStorage.removeItem('ase_token');
    localStorage.removeItem('ase_user');
    window.location.href = '/login';
}

function handleLogout() {
    localStorage.removeItem('ase_token');
    localStorage.removeItem('ase_user');
    window.location.href = '/login';
}

function initUserInfo() {
    const user = JSON.parse(localStorage.getItem('ase_user') || '{}');
    const nameEl = document.getElementById('user-name-display');
    if (nameEl && user.display_name) {
        nameEl.textContent = user.display_name;
    } else if (nameEl && user.username) {
        nameEl.textContent = user.username;
    }
}
