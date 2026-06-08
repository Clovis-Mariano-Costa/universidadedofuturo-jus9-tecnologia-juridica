(function(){
  var panels = document.querySelectorAll('[data-auth-central]');
  if (!panels.length) return;

  var authOrigin = 'https://jus9tecnologia.com.br';

  function loginUrl(){
    return authOrigin + '/auth/google/start?return_to=' + encodeURIComponent(location.href);
  }

  function render(panel, message, authenticated, permissions, identity){
    var status = panel.querySelector('[data-auth-status]');
    var login = panel.querySelector('[data-auth-login]');
    var list = panel.querySelector('[data-auth-permissions]');
    var context = panel.querySelector('[data-auth-identity]');
    if (status) status.textContent = message;
    if (login) login.href = loginUrl();
    if (list) {
      list.innerHTML = '';
      (permissions || []).forEach(function(item){
        var span = document.createElement('span');
        span.className = 'badge';
        span.textContent = item;
        list.appendChild(span);
      });
      list.hidden = !authenticated || !(permissions || []).length;
    }
    if (context) {
      context.textContent = identity ? [
        identity.profile && identity.profile.label,
        identity.origin && identity.origin.label,
        identity.user && identity.user.label
      ].filter(Boolean).join(' | ') : '';
      context.hidden = !context.textContent;
    }
  }

  async function load(panel){
    try {
      var me = await fetch(authOrigin + '/api/auth/me', { credentials:'include', cache:'no-store' });
      if (!me.ok) {
        render(panel, 'Sem sessao Google ativa. Entre com uma conta autorizada para estudo governado.', false, []);
        return;
      }
      var session = await me.json();
      var permissionsResponse = await fetch(authOrigin + '/api/auth/permissions', { credentials:'include', cache:'no-store' });
      var permissionsPayload = permissionsResponse.ok ? await permissionsResponse.json() : {};
      var contextResponse = await fetch(authOrigin + '/api/auth/context?origin=' + encodeURIComponent(location.origin), { credentials:'include', cache:'no-store' });
      var contextPayload = contextResponse.ok ? await contextResponse.json() : {};
      render(panel, 'Sessao ativa. Perfil operacional: ' + (session.profile || 'nao informado') + '.', true, permissionsPayload.permissions || [], contextPayload.identity || null);
    } catch (_) {
      render(panel, 'Nao foi possivel verificar a sessao agora. Mantenha uso demonstrativo.', false, [], null);
    }
  }

  panels.forEach(load);
})();
