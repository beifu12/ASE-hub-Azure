"use strict";
let articles = [];
let activeDomain = "ALL";
let activeService = "ALL";
let activeArticle = null;
const els = {
  search: document.getElementById("searchInput"),
  services: document.getElementById("serviceList"),
  results: document.getElementById("resultList"),
  count: document.getElementById("resultCount"),
  hint: document.getElementById("activeHint"),
  body: document.getElementById("articleBody"),
  meta: document.getElementById("articleMeta"),
  copy: document.getElementById("copyLink")
};

function norm(s){return String(s||"").toLowerCase();}
function currentQuery(){return els.search.value.trim().toLowerCase();}
function filtered(){
  const q = currentQuery();
  return articles.filter(a => {
    if(activeDomain !== "ALL" && a.domain !== activeDomain) return false;
    if(activeService !== "ALL" && a.service !== activeService) return false;
    if(!q) return true;
    const hay = norm([a.title,a.domain,a.service,a.section,a.summary,a.searchText].join(" "));
    return q.split(/\s+/).every(part => hay.includes(part));
  });
}

function renderServices(){
  const counts = new Map();
  for(const a of articles){
    if(activeDomain !== "ALL" && a.domain !== activeDomain) continue;
    const key = a.service || "未分类";
    counts.set(key,(counts.get(key)||0)+1);
  }
  const rows = [["ALL", articles.filter(a => activeDomain === "ALL" || a.domain === activeDomain).length], ...Array.from(counts.entries()).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0],"zh-Hans-CN"))];
  els.services.innerHTML = rows.map(([name,count]) => '<button class="service '+(activeService===name?'active':'')+'" data-service="'+name.replace(/"/g,"&quot;")+'"><span>'+name+'</span><span>'+count+'</span></button>').join("");
}

function renderResults(){
  const list = filtered();
  els.count.textContent = list.length + " 篇 KB";
  els.results.innerHTML = list.slice(0,300).map(a => {
    const active = activeArticle && activeArticle.id === a.id ? " active" : "";
    const summary = a.summary || a.searchText.slice(0,120);
    return '<button class="result-card'+active+'" data-id="'+a.id+'"><h3>'+escapeHtml(a.title)+'</h3><p>'+escapeHtml(summary)+'</p><div class="chips"><span class="chip">'+escapeHtml(a.domain)+'</span><span class="chip">'+escapeHtml(a.service)+'</span><span class="chip">'+escapeHtml(a.section)+'</span></div></button>';
  }).join("") || '<div class="result-card"><h3>没有匹配结果</h3><p>换一个关键词或清空筛选。</p></div>';
}

function escapeHtml(s){return String(s||"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));}

async function openArticle(id, push=true){
  const a = articles.find(x => x.id === id);
  if(!a) return;
  activeArticle = a;
  const html = await fetch(a.href).then(r => r.text());
  els.body.className = "article-body";
  els.body.innerHTML = html;
  els.meta.textContent = [a.domain, a.service, a.section, a.modified].filter(Boolean).join(" / ");
  els.hint.textContent = a.title;
  if(push) history.replaceState(null,"","#"+encodeURIComponent(id));
  renderResults();
}

function bind(){
  document.querySelectorAll(".filter").forEach(btn => btn.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeDomain = btn.dataset.domain;
    activeService = "ALL";
    renderServices();
    renderResults();
  }));
  els.search.addEventListener("input", () => renderResults());
  els.services.addEventListener("click", e => {
    const btn = e.target.closest(".service");
    if(!btn) return;
    activeService = btn.dataset.service;
    renderServices();
    renderResults();
  });
  els.results.addEventListener("click", e => {
    const btn = e.target.closest(".result-card[data-id]");
    if(btn) openArticle(btn.dataset.id);
  });
  els.copy.addEventListener("click", async () => {
    const url = location.href;
    try { await navigator.clipboard.writeText(url); els.copy.textContent = "已复制"; setTimeout(()=>els.copy.textContent="复制链接",1200); }
    catch { prompt("复制链接", url); }
  });
}

fetch("kb-index.json").then(r => r.json()).then(data => {
  articles = data;
  bind();
  renderServices();
  renderResults();
  const id = decodeURIComponent(location.hash.replace(/^#/,""));
  if(id) openArticle(id, false);
});