(function(){
  window.addEventListener('DOMContentLoaded', function(){
    var btn = document.getElementById('nav-toggle');
    var menu = document.getElementById('mobile-menu');
    if (!btn || !menu) return;
    btn.addEventListener('click', function(){
      menu.classList.toggle('hidden');
    });
  });
})();
