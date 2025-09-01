(function(){
  try {
    const root = document.documentElement; // <html>
    const stored = localStorage.getItem('color-mode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = stored || (prefersDark ? 'dark' : 'light');
    root.setAttribute('data-bs-theme', initial);
    window.addEventListener('DOMContentLoaded', function(){
      const btn = document.getElementById('theme-toggle');
      if(!btn) return;
      btn.addEventListener('click', function(){
        const current = root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-bs-theme', next);
        localStorage.setItem('color-mode', next);
      });
    });
  } catch(e) {}
})();
