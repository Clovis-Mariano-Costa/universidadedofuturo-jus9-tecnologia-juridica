# PLAT-01 — Contrato backend e estados V1

## Escopo

Pacote local, determinístico e sem integração externa para consolidar o núcleo comum dos pedidos Backend V2.0, V3.0 e V4.0. A implementação vive em `codex-governance.mjs` e não cria API pública, banco, sincronização Drive/GitHub, titulação ou efeito jurídico.

## Contratos implementados

- `validateMaoNaMassaTransition`: máquina de estados `PREPARAR -> EMBRULHAR -> VALIDAR -> APROVAR -> EXECUTAR -> AUDITAR`, com `ROLLBACK` e `BLOQUEAR` como saídas explícitas. Toda transição exige agente, evidência e rollback; aprovação/execução exigem `human_gate=true`.
- `createProvenanceRecord`: exige origem, atividade, agente, versão, hash, rota e rollback; não aceita registro sem trilha mínima.
- `assertFinalApprovalGate`: bloqueia aprovação final quando falta aprovação humana, banca plural, hash comum dos pareceristas ou evidência empírica exigida.
- `createCtpsvMergeProposal`: aceita somente proposta profissional explicitamente versionada e rejeita nomes de campos domésticos/sensíveis; inicia em `PENDENTE_REVISAO_TITULAR`.

## Preservação e limites

O pacote não altera MGP9 V1/V1.2, corpus, método, POC, CTPSV real, Casa-Lar, Casa-Trabalho ou rotas públicas. Não simula assinatura humana, não promove especialidade/titulação e não faz merge automático de dados.

## Verificação e rollback

Executar `npm test` em `CODEX/runtime`. O rollback é a reversão do commit deste pacote; os contratos são funções puras e não criam estado externo.
