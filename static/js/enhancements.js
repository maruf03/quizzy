// jQuery enhancements: dynamic formset, auto-dismiss alerts, leaderboard flashes
$(function() {
  // Auto dismiss alerts after 5s
  setTimeout(function(){ $('.alert').not('.alert-important').fadeOut(400, function(){ $(this).remove(); }); }, 5000);

  // Dynamic answer formset (Question edit page)
  const formsetContainer = $('[data-formset="answers"]');
  if(formsetContainer.length){
    const prefix = formsetContainer.data('prefix');
    const totalInput = $('#id_' + prefix + '-TOTAL_FORMS');
  const emptyHolder = $('#answer-empty');
    window.__answersEnhanced = true;
    function addForm(){
      const index = parseInt(totalInput.val(), 10);
      if(!emptyHolder.length){ console.error('[Answers] empty template not found'); return; }
      let html = emptyHolder.html().replace(/__prefix__/g, index);
      const el = $(html);
      el.attr('data-index', index);
      el.addClass('fade-scale-in');
      formsetContainer.append(el);
      totalInput.val(index + 1);
      el.on('animationend', ()=> el.removeClass('fade-scale-in'));
    }
    $('#add-answer').on('click', addForm);
    formsetContainer.on('click', '.remove-row', function(){
      const card = $(this).closest('.formset-item');
      const deleteBox = card.find('input[type=checkbox][name$="-DELETE"]');
      if(deleteBox.length){ deleteBox.prop('checked', true); }
      // Remove required so browser doesn't block submit
      card.find(':input[required]').removeAttr('required');
      card.addClass('fade-collapse-out');
      card.on('animationend', () => { card.hide(); });
    });
    // Client-side validation before submit
    $('form').on('submit', function(e){
      const rows = formsetContainer.children('.formset-item').filter(function(){
        const hidden = $(this).find('input[type=checkbox][name$="-DELETE"]');
        return !(hidden.length && hidden.prop('checked'));
      });
      let answerCount = 0, correctCount = 0;
      rows.each(function(){
        const txt = $(this).find('input[type=text]').val().trim();
        if(txt){
          answerCount++;
          if($(this).find('input[type=checkbox][name$="-is_correct"]').is(':checked')) correctCount++;
        }
      });
      if(answerCount < 2 || correctCount < 1){
        e.preventDefault();
        alert('Need at least two answers and one marked correct.');
      }
    });
  }

  // Leaderboard highlight (expects rows with data-score)
  window.flashLeaderboard = function(entries) {
    entries.forEach(e => {
      const row = $("[data-leaderboard-user='"+ (e.user || e.user_id) +"']");
      if(row.length){
        row.addClass('table-warning');
        setTimeout(()=> row.removeClass('table-warning'), 1500);
      }
    });
  };
  // Auto-connect leaderboard if container exists
  const lb = $('#live-leaderboard[data-quiz]');
  if(lb.length){
    const quizId = lb.data('quiz');
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    try {
      const sock = new WebSocket(protocol + '://' + location.host + '/ws/quizzes/' + quizId + '/leaderboard/');
      sock.onopen = function(){ console.log('[LB] websocket connected'); };
      sock.onerror = function(e){ console.error('[LB] websocket error', e); };
      sock.onclose = function(){ console.warn('[LB] websocket closed'); };
      sock.onmessage = function(ev){
        try {
          const data = JSON.parse(ev.data);
          if(data.type==='leaderboard'){
            renderLeaderboard(data.entries || []);
            flashLeaderboard(data.entries || []);
          }
        } catch(err){ console.error('[LB] message parse error', err); }
      };
    } catch(err){ console.error('[LB] websocket init failed', err); }
  }

  function relTime(iso){
    if(!iso) return '';
    const d = new Date(iso);
    const now = new Date();
    const diff = (now - d) / 1000; // seconds
    if(diff < 5) return 'just now';
    if(diff < 60) return Math.floor(diff) + 's ago';
    const m = diff/60;
    if(m < 60) return Math.floor(m) + 'm ago';
    const h = m/60;
    if(h < 24) return Math.floor(h) + 'h ago';
    const days = h/24;
    if(days < 7) return Math.floor(days) + 'd ago';
    return d.toLocaleDateString();
  }

  function renderLeaderboard(entries){
    const tbody = $('#leaderboard-table tbody');
    tbody.empty();
    if(!entries.length){
      tbody.append('<tr><td colspan="5" class="text-body-secondary small">No scores yet.</td></tr>');
      return;
    }
    entries.forEach((e,i)=>{
      const row = $('<tr>')
        .attr('data-leaderboard-user', e.user)
        .append('<td>' + (i+1) + '</td>')
        .append('<td>' + e.user + '</td>')
        .append('<td class="text-end fw-semibold">' + e.score + '</td>')
        .append('<td class="text-end small">' + e.attempt + '</td>')
        .append('<td class="small" data-reltime="' + e.submitted_at + '">' + relTime(e.submitted_at) + '</td>');
      tbody.append(row);
    });
  }

  // Periodically refresh relative times (in case user leaves page open)
  setInterval(function(){
    $('[data-reltime]').each(function(){
      const iso = $(this).data('reltime');
      $(this).text(relTime(iso));
    });
  }, 60000);
});

// Lightweight vanilla fallback if jQuery failed to load
if(typeof window.jQuery === 'undefined'){
  document.addEventListener('DOMContentLoaded', function(){
    const container = document.querySelector('[data-formset="answers"]');
    if(!container) return;
    const prefix = container.getAttribute('data-prefix');
    const totalInput = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
    const proto = document.getElementById('answer-prototype');
    if(!totalInput || !proto) return;
    function add(){
      const idx = parseInt(totalInput.value, 10);
      let html = proto.innerHTML.replace(/__prefix__/g, idx);
      const wrapper = document.createElement('div');
      wrapper.className = 'card mb-2 formset-item fade-scale-in';
      wrapper.dataset.index = idx;
      wrapper.innerHTML = html;
      container.appendChild(wrapper);
      totalInput.value = idx + 1;
      wrapper.addEventListener('animationend', ()=> wrapper.classList.remove('fade-scale-in'));
    }
    const addBtn = document.getElementById('add-answer');
    if(addBtn) addBtn.addEventListener('click', add);
    container.addEventListener('click', function(e){
      const btn = e.target.closest('.remove-row');
      if(!btn) return;
      const card = btn.closest('.formset-item');
      const del = card.querySelector('input[name$="-DELETE"]');
      if(del) del.checked = true;
      card.querySelectorAll('[required]').forEach(el=> el.removeAttribute('required'));
      card.classList.add('fade-collapse-out');
      card.addEventListener('animationend', ()=> card.style.display='none');
    });
  });
}
