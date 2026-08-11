# Relatório de implementação — Automação da Universidade do Futuro V1

**Pedido:** `CODEX/para_codex_programar/PEDIDO_CODEX_UNIVERSIDADE_PESQUISA_EXTENSAO_ADJUDICACAO_V1_0.md`  
**Estado:** `CONCLUIDO_LOCALMENTE / SEM_MERGE / SEM_DEPLOY`  
**Data:** 11/08/2026 — America/Sao_Paulo  
**Natureza:** sandbox offline, sintético e não estatal

## Entrega

`UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/`

O sandbox implementa:

- registry normativo versionado com SHA-256;
- proteção `READ_ONLY_BY_DEFAULT` para normas protegidas;
- fluxo de atualização protegido com `human_gate` e `constitutional_flow`;
- registry de pesquisa/extensão com estado, fontes, ética, dados, pré-registro, execução, evidência, impacto, devolutiva e hash;
- adjudicação experimental interna com conflito, evidência, revisão, rollback e jurisdição `INTERNAL_EXPERIMENTAL`;
- bloqueio de efeito externo;
- quarentena de fonte sem identificador verificável;
- linter de status, hash protegido, referência quebrada e falsa autoridade externa;
- eventos de proveniência append-only encadeados por hash;
- ponte dry-run somente leitura entre MGP9, Pacote 12 ASM/GHR/GV e decisão universitária interna;
- workflow sequencial de pesquisa e extensão com gates humanos;
- contraditório, votos, fundamentação, revisão e recurso interno na adjudicação;
- regra de precedência normativa G6 com bloqueio de empate;
- scanner sintético de segredo/PII, segregação de tenant, menor privilégio e gate `APTO_NO_ESCOPO`;
- material didático para Charlie Echo.

## Evidência de teste

Comando executado na raiz do repositório:

```powershell
python -m unittest discover -s UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/tests -v
```

Resultado anterior: **9 testes aprovados**. A ponte e os controles de workflow/segurança adicionaram 13 testes, totalizando **22 testes aprovados** no sandbox universitário.

Casos cobertos: mutação de norma protegida; fluxo constitucional; precedência G6; empate normativo; quarentena; registry de pesquisa; workflow completo; workflow de extensão; conflito; contraditório; votos; fundamentação; recurso interno; jurisdição externa; gate humano; decisão interna; rollback append-only; linter; cadeia de hashes; scanner de segredo/PII; menor privilégio; segregação; incidente; composição válida; hash MGP9 ausente; gate Pacote 12 bloqueado; decisão externa; evento append-only da ponte.

## Auditoria dos sandboxes anteriores

- MGP9: registry PASS; 4 testes PASS; smoke PASS; 72 pares disponíveis.
- Pacote 12 ASM/GHR/GV: 9 testes PASS; `git diff --check` PASS.
- Universidade Automação: 14 testes PASS; `git diff --check` PASS.
- BJI Validation: 5 testes PASS; estado permanece `NAO_EXECUTADO`.

## Ponte dry-run

`UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/bridge.py` aceita apenas evidências sintéticas e compõe os três sandboxes em memória. A ponte falha fechado e produz exclusivamente `READY_FOR_HUMAN_REVIEW` ou `BLOCKED`, sempre com `external_effect=False`. Não grava arquivo, não acessa rede, não altera registry e não autoriza publicação.

`BJI_VALIDATION_SANDBOX_V1/` prepara metadados reprodutíveis sem executar experimento ou fabricar resultado. Seu estado de aceite é `NAO_EXECUTADO`.

## Limites

Não houve acesso a Drive, GitHub via código, rede, credenciais, normas reais, dados pessoais, publicação, merge, deploy, decisão estatal, banca ou homologação. O sandbox não demonstra validade jurídica nem altera cláusula pétrea. O próximo gate é revisão humana dos contratos, pré-registro e autorização de integração antes de qualquer corpus real.

**Regra:** teste sintético aprovado não é autorização externa.
