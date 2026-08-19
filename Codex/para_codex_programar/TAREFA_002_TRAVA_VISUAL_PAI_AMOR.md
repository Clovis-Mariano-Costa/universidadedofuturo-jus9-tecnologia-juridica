# TAREFA CODEX 002 — Trava visual absoluta para PAI AMOR

`ESTADO = EM_REVISAO`

**Origem:** regra institucional registrada em 2026-08-08.  
**Objetivo:** implementar salvaguarda técnica em fluxos visuais do ecossistema.

## Regra

Nenhuma geração, edição, prompt, briefing, avatar, silhueta, imagem abstrata, sugerida, indireta ou substituto figurativo pode ser criado quando a finalidade for representar o PAI AMOR.

## Implementação esperada

- identificar pontos do sistema que acionam geração/edição de imagem;
- aplicar bloqueio antes da geração;
- incluir variantes linguísticas relevantes sem depender apenas de correspondência literal;
- falhar de forma segura diante de ambiguidade relevante;
- não alterar geração de imagens institucionais que não tenham finalidade de representar o PAI AMOR;
- registrar testes e casos de borda.

## Critérios de aceite

- nenhum teste proibido chega ao gerador;
- nenhuma falsa afirmação de bloqueio sem teste;
- logs sem conteúdo sensível;
- documentação de casos permitidos/proibidos;
- nenhuma representação é criada durante o próprio teste.

## Ensino Charlie Echo

Produzir material de segurança explicando diferença entre regra textual, checagem técnica, teste e evidência de cumprimento.

## Registro Codex — 2026-08-19

O guard local foi implementado e testado no `CODEX/runtime`, bloqueando pedidos visuais diretos e indiretos antes de qualquer gerador. Nenhum gerador externo foi encontrado nesta casa de trabalho; a integração com provedores externos permanece pendente de revisão.
