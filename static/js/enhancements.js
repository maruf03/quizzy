// jQuery enhancements: dynamic formset, auto-dismiss alerts, leaderboard flashes
$(function() {
  // Auto dismiss alerts after 5s
  setTimeout(function(){ $('.alert').not('.alert-important').fadeOut(400, function(){ $(this).remove(); }); }, 5000);

  // Dynamic answer formset (Question edit page)
  const formsetContainer = $('[data-formset="answers"]');
  if(formsetContainer.length){
    const prefix = formsetContainer.data('prefix');
    const totalInput = $('#id_' + prefix + '-TOTAL_FORMS');
    $('#add-answer').on('click', function(){
      const currentTotal = parseInt(totalInput.val(), 10);
      const lastItem = formsetContainer.children('.formset-item').last();
      const newIndex = currentTotal;
      const clone = lastItem.clone(false);
      clone.attr('data-index', newIndex);
      clone.find(':input').each(function(){
        const oldName = $(this).attr('name');
        if(!oldName) return;
        const newName = oldName.replace(/-(\d+)-/, '-' + newIndex + '-');
        const newId = 'id_' + newName;
        $(this).attr({'name': newName, 'id': newId});
        if($(this).is(':checkbox')){
          $(this).prop('checked', false);
        } else {
          $(this).val('');
        }
      });
      clone.find('.delete-field :checkbox').prop('checked', false);
      clone.find('.remove-row').prop('disabled', false);
      formsetContainer.append(clone.hide().fadeIn(150));
      totalInput.val(currentTotal + 1);
    });
    formsetContainer.on('click', '.remove-row', function(){
      const item = $(this).closest('.formset-item');
      const deleteBox = item.find('.delete-field :checkbox');
      if(deleteBox.length){
        deleteBox.prop('checked', true);
        item.fadeOut(150);
      } else {
        item.fadeOut(150, function(){ $(this).remove(); });
        const currentTotal = parseInt(totalInput.val(), 10) - 1;
        totalInput.val(currentTotal);
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
