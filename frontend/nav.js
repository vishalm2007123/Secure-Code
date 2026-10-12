// nav.js — Shared navigation logic for all pages
const API_URL = "http://127.0.0.1:8000";

// Set active nav link based on current page
(function() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  const map = { 'index.html':'home', '':'home', 'auditor.html':'auditor', 'studio.html':'studio', 'analytics.html':'analytics', 'docs.html':'docs' };
  const cur = map[path] || 'home';
  document.querySelectorAll('.nav-link').forEach(l => {
    if (l.getAttribute('data-page') === cur) l.classList.add('active');
    else l.classList.remove('active');
  });
})();

// Theme system
function initTheme() {
  const saved = localStorage.getItem('securecode_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-theme');
      const next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('securecode_theme', next);
    });
  }
}

// Live health check
async function checkHealth() {
  const dot = document.querySelector('.status-dot');
  const label = document.querySelector('.status-label');
  try {
    const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(4000) });
    if (res.ok) {
      const d = await res.json();
      if (label) label.textContent = d.ollama_online ? `Engine Ready — ${d.ollama_model}` : 'Engine Online (AST Mode)';
      if (dot) { dot.style.background = 'var(--state-safe)'; dot.style.boxShadow = '0 0 6px var(--state-safe)'; }
    }
  } catch {
    if (label) label.textContent = 'Standalone Mode';
    if (dot) { dot.style.background = 'var(--severity-medium)'; dot.style.boxShadow = '0 0 6px var(--severity-medium)'; }
  }
}

// Helper
function escapeHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

document.addEventListener('DOMContentLoaded', () => { initTheme(); checkHealth(); });
