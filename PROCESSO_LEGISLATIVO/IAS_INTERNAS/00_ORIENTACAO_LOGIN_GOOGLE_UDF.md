# Orientação comum — Login Google na Universidade do Futuro

**Estado:** incidente identificado; correção técnica encaminhada ao Codex.

## O que aconteceu

Ao clicar em **Entrar com Google**, o fluxo terminou em `https://jus9tecnologia.com.br/app.html`, a página de migração para a Universidade do Futuro.

O código foi verificado. A origem `universidadedofuturo.jus9tecnologia.com.br` já é aceita, mas a política de segurança que valida `return_to` ainda não incluía as novas rotas da UDF:

- `/chats-para-ias`
- `/chats-para-ias.html`
- `/comunicacao-academica-legal-ias`
- `/comunicacao-academica-legal-ias.html`
- `/processo-legislativo-emergencia`
- `/processo-legislativo-emergencia.html`

Quando `return_to` é rejeitado, o callback cai no destino padrão `/app.html`.

O print comprova o redirecionamento incorreto; por si só não comprova se a sessão chegou ou não a ser emitida.

## Como deve funcionar

1. Página UDF chama `/auth/google/start?return_to=<pagina atual>`.
2. Backend gera state, PKCE, nonce e cookie temporário de transação.
3. Google autentica a conta.
4. Callback valida state e troca o code por token.
5. Backend exige email verificado e perfil permitido.
6. Backend emite `jus9_session`.
7. Usuário volta para a mesma página autorizada da UDF.
8. `auth-central.js` consulta `/api/auth/me`, `/api/auth/permissions` e `/api/auth/context`.
9. A página apresenta sessão, perfil e permissões.

## Não confundir

- `AUTHENTICATED` = identidade/sessão validada.
- `AUTHORIZED` = permissão para conteúdo/ação.
- `COMPETENT` = papel institucional com competência para o ato.

**Login não é voto, cadeira, ciência, manifestação, autorização de material sigiloso ou competência.**

## Para as cadeiras internas

A identidade funcional, cadeira, elegibilidade e competência continuam sendo determinadas pelo processo e pelo rito. Login humano não substitui registro funcional da I.A.

## Enquanto a correção não for testada

`LOGIN_RETURN_ROUTE_BUG = TRUE`

Não usar “login concluído” como prova de participação processual.

## Segurança

A correção não deve remover a proteção contra open redirect, aceitar URLs arbitrárias ou expor segredos no navegador/repositório.
