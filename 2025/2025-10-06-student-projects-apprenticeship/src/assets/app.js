
/* Global JS for GradeBridge Project Hub */
(function(){
  const injectPartial = async (id, url) => {
    const container = document.getElementById(id);
    if (!container) return;
    try {
      const res = await fetch(url);
      const html = await res.text();
      container.innerHTML = html;
      if (id === 'headerMount') afterHeaderInject();
    } catch (e) { console.error('Failed to load partial', url, e); }
  };

  // Theme
  const THEME_KEY = 'gb.theme';
  function applyTheme(theme){
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-bs-theme','dark');
    } else {
      document.documentElement.removeAttribute('data-bs-theme');
    }
  }
  const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(savedTheme);

  // After header inject: wire up search & theme toggle
  function afterHeaderInject(){
    // Active nav highlighting
    const page = document.body.dataset.page || '';
    document.querySelectorAll('#siteNavbar a.nav-link').forEach(a=>{
      const key = a.getAttribute('data-nav');
      if (key && page.startsWith(key)) a.classList.add('active');
    });

    const btnToggle = document.getElementById('themeToggle');
    if (btnToggle) btnToggle.addEventListener('click', ()=>{
      const next = (localStorage.getItem(THEME_KEY) || 'light') === 'light' ? 'dark' : 'light';
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });

    // Search offcanvas
    const offcanvasEl = document.getElementById('offcanvasSearch');
    const offcanvas = offcanvasEl ? new bootstrap.Offcanvas(offcanvasEl) : null;
    const btnSearch = document.getElementById('btnSearchIcon');
    const btnSearchGo = document.getElementById('offcanvasSearchGo');
    const input2 = document.getElementById('offcanvasSearchInput');

    const runSearch = async (q) => {
      if (!q || q.trim().length < 2) return;
      const pages = [
        {url:'index.html', title:'Overview'},
        {url:'sprints.html', title:'Sprint Planning'},
        {url:'tasks.html', title:'Task Breakdown'},
        {url:'api.html', title:'API Implementation'},
        {url:'data-model.html', title:'Database Design'},
        {url:'ui.html', title:'Frontend Development'},
        {url:'security.html', title:'Security Guidelines'},
        {url:'testing.html', title:'Testing Strategy'},
        {url:'decisions.html', title:'Architecture Decisions'},
        {url:'roadmap.html', title:'Product Evolution'},
      ];
      const results = [];
      for (const p of pages) {
        try {
          const res = await fetch(p.url);
          const txt = await res.text();
          // Grab main content only if possible
          const m = txt.match(/<main[^>]*>([\s\S]*?)<\/main>/i);
          const content = (m ? m[1] : txt).replace(/<[^>]+>/g,' ');
          const idx = content.toLowerCase().indexOf(q.toLowerCase());
          if (idx !== -1) {
            const start = Math.max(0, idx-60);
            const end = Math.min(content.length, idx+120);
            const snippet = content.substring(start, end).replace(/\s+/g,' ').trim();
            results.push({title:p.title, url:p.url, snippet});
          }
        } catch (e) { /* ignore */ }
      }
      const list = document.getElementById('searchResults');
      if (list) {
        list.innerHTML = '';
        if (!results.length) {
          list.innerHTML = '<div class="text-muted">No results.</div>';
        } else {
          results.forEach(r=>{
            const a = document.createElement('a');
            a.href = r.url + '#search';
            a.className = 'list-group-item list-group-item-action';
            a.innerHTML = `<div class="fw-semibold">${r.title}</div><div class="small text-muted">${r.snippet}…</div>`;
            list.appendChild(a);
          });
        }
      }
    };

    if (btnSearch) btnSearch.addEventListener('click', ()=> { if (offcanvas) offcanvas.show(); setTimeout(()=>input2?.focus(), 300); });
    if (btnSearchGo && input2) btnSearchGo.addEventListener('click', ()=> runSearch(input2.value));
    input2?.addEventListener('keydown', (e)=> { if (e.key === 'Enter') runSearch(input2.value); });
  }

  // Inject header and footer into mounts
  document.addEventListener('DOMContentLoaded', ()=>{
    injectPartial('headerMount', 'partials/header.html');
    injectPartial('footerMount', 'partials/footer.html');
  });

  // Utility: copy text
  window.copyText = async function copyText(txt){
    try {
      await navigator.clipboard.writeText(txt);
      alert('Copied to clipboard!');
    } catch (e) {
      console.log('Clipboard failed', e);
    }
  };

})();
