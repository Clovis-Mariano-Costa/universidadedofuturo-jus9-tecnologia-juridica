(function(){
  const input=document.getElementById('sagrado-question');
  const send=document.getElementById('sagrado-send');
  const out=document.getElementById('sagrado-response');
  if(!input||!send||!out)return;

  const MAX_QUESTION_CHARS=4000;
  let inFlight=false;

  function escapeHtml(text){
    return String(text||'').replace(/[&<>"]/g,function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch];
    });
  }

  function linkify(text){
    return escapeHtml(text)
      .replace(/https:\/\/[^\s<>"']+/g,function(raw){
        let url=raw,suffix='';
        while(/[),.;:!?]$/.test(url)){suffix=url.slice(-1)+suffix;url=url.slice(0,-1);}
        return '<a href="'+url+'" target="_blank" rel="noopener noreferrer">'+url+'</a>'+suffix;
      })
      .replace(/\n/g,'<br>');
  }

  function render(text){out.innerHTML=linkify(text);}

  function requestId(){
    if(globalThis.crypto&&typeof globalThis.crypto.randomUUID==='function'){
      return 'sagrado-'+globalThis.crypto.randomUUID();
    }
    return 'sagrado-'+Date.now().toString(36);
  }

  function sacredMessage(question){
    return [
      'AMBIENTE: Chat do Sagrado da Universidade do Futuro.',
      'PAPEL: responda como Charlie Echo, I.A. de estudo e reflexão. Não se apresente como Sacerdote.',
      'REGRAS: preserve liberdade de crença e não crença; não presuma adesão religiosa; diferencie fonte, tradição, interpretação e reflexão de I.A.; não alegue revelação, profecia, milagre ou certeza transcendente como fato demonstrado; não transforme orientação religiosa em lei ou efeito institucional.',
      'PRIVACIDADE: não solicite segredos, tokens, senhas, dados sigilosos ou confissões íntimas.',
      'PEDIDO DO USUÁRIO:',
      question
    ].join('\n\n');
  }

  async function ask(){
    if(inFlight)return;
    const question=input.value.trim();

    if(!question){
      render('Escreva uma pergunta para iniciar o estudo.');
      input.focus();
      return;
    }
    if(question.length>MAX_QUESTION_CHARS){
      render('A pergunta ultrapassa o limite de 4.000 caracteres. Divida o texto em partes menores.');
      input.focus();
      return;
    }

    inFlight=true;
    send.disabled=true;
    send.setAttribute('aria-busy','true');
    out.setAttribute('aria-busy','true');
    render('Charlie Echo está estudando sua pergunta...');

    const controller=new AbortController();
    const timeout=setTimeout(function(){controller.abort();},20000);

    try{
      const res=await fetch('https://charlieecho.jus9tecnologia.com.br/api/ia',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        signal:controller.signal,
        body:JSON.stringify({
          requestId:requestId(),
          mode:'estudantes',
          message:sacredMessage(question),
          room:{
            id:'sagrado-publico',
            title:'Chat do Sagrado',
            currentTopic:'estudo e reflexão do Sagrado'
          }
        })
      });

      const contentType=res.headers.get('content-type')||'';
      if(!res.ok)throw new Error('HTTP '+res.status);
      if(!contentType.includes('application/json'))throw new Error('Resposta não JSON');

      const data=await res.json();
      if(!data||data.ok!==true||typeof data.answer!=='string'||!data.answer.trim()){
        throw new Error('Contrato de resposta inválido');
      }

      render(data.answer.trim());
    }catch(err){
      if(err&&err.name==='AbortError'){
        render('A tentativa excedeu o tempo local. O navegador deixou de aguardar, mas o resultado remoto pode ser desconhecido. Não vou repetir automaticamente o envio.');
      }else{
        render('A resposta remota não pôde ser confirmada nesta tentativa. Nada foi registrado como ensinamento recebido e o envio não será repetido automaticamente.');
      }
    }finally{
      clearTimeout(timeout);
      inFlight=false;
      send.disabled=false;
      send.removeAttribute('aria-busy');
      out.removeAttribute('aria-busy');
    }
  }

  send.addEventListener('click',ask);
  input.addEventListener('keydown',function(event){
    if(event.key==='Enter'&&(event.ctrlKey||event.metaKey)){
      event.preventDefault();
      ask();
    }
  });
})();