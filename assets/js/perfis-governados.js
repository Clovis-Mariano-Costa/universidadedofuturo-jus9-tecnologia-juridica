(function(){
  var storageKey = 'jus9UniversidadePerfisGovernadosV1';
  var forms = document.querySelectorAll('[data-local-profile-form]');
  var drafts = document.querySelector('[data-profile-drafts]');
  var authOrigin = 'https://jus9tecnologia.com.br';
  if(!forms.length) return;

  function read(){
    try { return JSON.parse(localStorage.getItem(storageKey) || '[]'); }
    catch(_) { return []; }
  }

  function write(items){
    try { localStorage.setItem(storageKey, JSON.stringify(items.slice(0, 80))); }
    catch(_) {}
  }

  function escapeHtml(text){
    return String(text || '').replace(/[<>&"]/g, function(ch){
      return ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[ch]);
    });
  }

  function render(){
    if(!drafts) return;
    var items = read();
    if(!items.length){
      drafts.innerHTML = '<p class="small">Nenhum rascunho local salvo ainda.</p>';
      return;
    }
    drafts.innerHTML = items.map(function(item){
      return '<article class="card"><strong>' + escapeHtml(item.name) + '</strong><p>' +
        escapeHtml(item.email) + ' | ' + escapeHtml(item.scope) + ' | ' + escapeHtml(item.profile) +
        '</p><p class="small">' + escapeHtml(item.module || 'sem area') +
        (item.remoteId ? ' | protocolo: ' + escapeHtml(item.remoteId) : '') + '</p></article>';
    }).join('');
  }

  function statusFor(form){
    var status = form.querySelector('[data-profile-submit-status]');
    if(!status){
      status = document.createElement('p');
      status.className = 'small';
      status.setAttribute('data-profile-submit-status', '');
      form.appendChild(status);
    }
    return status;
  }

  async function submitGoverned(item){
    var response = await fetch(authOrigin + '/api/profile-requests', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scope: item.scope,
        name: item.name,
        email: item.email,
        profile: item.profile,
        module: item.module,
        notes: item.notes,
        imagePolicy: item.hasImageDraft ? 'imagem_recebida_apenas_como_sinal_local_para_revisao' : 'sem_imagem'
      })
    });
    var payload = await response.json().catch(function(){ return null; });
    if(!response.ok || !payload || !payload.ok) {
      throw new Error((payload && (payload.error || payload.message)) || 'envio_nao_confirmado');
    }
    return payload;
  }

  forms.forEach(function(form){
    form.addEventListener('submit', async function(event){
      event.preventDefault();
      var data = new FormData(form);
      var item = {
        id: 'perfil-universidade-' + Date.now(),
        scope: form.getAttribute('data-profile-scope') || 'universidade',
        name: data.get('name') || '',
        email: data.get('email') || '',
        profile: data.get('profile') || '',
        module: data.get('module') || '',
        notes: data.get('notes') || '',
        hasImageDraft: !!(data.get('image') && data.get('image').name),
        createdAt: new Date().toISOString()
      };
      var items = read();
      items.unshift(item);
      write(items);
      var status = statusFor(form);
      status.textContent = 'Rascunho local salvo. Tentando registrar solicitacao governada...';
      try {
        var result = await submitGoverned(item);
        items = read().map(function(saved){
          if(saved.id !== item.id) return saved;
          saved.remoteId = result.id;
          saved.remoteStatus = result.status;
          return saved;
        });
        write(items);
        status.textContent = 'Solicitacao governada registrada para revisao humana: ' + result.id + '.';
      } catch (error) {
        status.textContent = 'Rascunho local salvo. Para envio governado, entre com Google autorizado. Motivo: ' + (error.message || 'sessao indisponivel') + '.';
      }
      form.reset();
      render();
    });
  });

  render();
})();
