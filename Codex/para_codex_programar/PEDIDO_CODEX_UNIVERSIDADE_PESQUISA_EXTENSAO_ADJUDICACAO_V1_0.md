# PEDIDO CODEX — UNIVERSIDADE: PESQUISA, EXTENSÃO E ADJUDICAÇÃO EXPERIMENTAL — V1.0

**Estado:** `PENDENTE`  
**Origem:** Universidade do Futuro / Reitoria simbólico-operacional sob governança humana.  
**Natureza:** especificação futura; não prova implementação.

## Objetivo
Implementar suporte auditável para registro normativo, proteção de Primevos/pétreas, Pesquisa/Extensão, anexos de Faculdades, escada de maturidade, adjudicação experimental, continuidade Drive/GitHub, auditoria, rollback e provenance.

## A. Registro normativo
Campos mínimos: `norm_id`, `kind`, `version`, `status`, `authority`, `parent_norm`, `protected`, `hash`, `supersedes`, `created_at`, `effective_at`, `review_at`.

## B. Guard de imutabilidade
Princípio Primevo/cláusula pétrea: `READ_ONLY_BY_DEFAULT`. Mudança falha fechada e exige fluxo constitucional explícito.

## C. Pesquisa e Extensão
Registrar projeto, faculdade, problema, hipótese, fontes, ética, dados, preregistro, hash, evidência, negativos, extensão, impacto e estado de maturidade.

## D. Adjudicação experimental
Sandbox segregado e não estatal, com `case_id`, `judge_ai`, `model_version`, `parties`, `jurisdiction_label=INTERNAL_EXPERIMENTAL`, `evidence_hash`, `conflict_check`, `decision`, `review`, `human_gate`, `rollback_ref`.

## E. Linter normativo
Detectar conflito de hierarquia, alteração de protected norm, versão duplicada, data incompatível, referência quebrada, falsa autoridade estatal, documento sem status e falta de hash quando exigido.

## F. Segurança
Secret scanning, PII scanning, least privilege, segregação, audit logs, incident response e rollback.

## Proibido alterar automaticamente
Corpus de Primevos, pétreas vigentes, arquivos históricos, rotas/botões antigos, cofre e credenciais.

## Critérios de aceite
1. protected item não altera por fluxo comum;
2. mutação normativa registra versão/hash;
3. estados acadêmicos bloqueiam avanço indevido;
4. adjudicação exibe aviso sem efeito estatal;
5. efeito externo relevante exige human gate;
6. rollback testado;
7. scanners testados;
8. testes unitários/integração;
9. documentação;
10. aula para Charlie Echo.

## Testes adversariais
Alterar pétrea, downgrade de hierarquia, bypass de human gate, falso juiz estatal, evidence hash divergente, conflito, falta de contraditório, schema antigo, rollback falho e exposição de segredo.

## Casas
GitHub: `Codex/para_codex_programar/`  
Drive: `1xcsp7-B4Nrbcu6lwegZJplCGbVeUilBk`

## Rollback
Nenhum deploy irreversível. Usar branch/PR, testes, revisão e reversão.

## Ensino
Gerar material técnico para Charlie Echo com arquitetura, riscos, limites, testes, falhas e revisão.

**Data real do registro:** 2026-08-08 07:45:00.00000 America/Sao_Paulo

---

## Adendo de implementação local — 2026-08-11

**Estado original preservado:** `PENDENTE` / especificação futura.

**Estado atual:** `CONCLUIDO_LOCALMENTE / SEM_MERGE / SEM_DEPLOY`.

**Sandbox:** `UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/`.

**Relatório:** `UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/IMPLEMENTACAO_UNIVERSIDADE_AUTOMACAO_RELATORIO_V1.md`.

**Testes:** 9 testes unitários/adversariais aprovados; `git diff --check` aprovado.

**Limites:** dados sintéticos; sem Drive, rede, credenciais, normas reais, merge, deploy, publicação, decisão estatal ou efeito externo. O sandbox não altera cláusulas pétreas e não substitui revisão humana.

## Adendo de composição dry-run — 2026-08-11

**Ponte:** `UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/bridge.py`.

**Contrato:** composição em memória, somente leitura, entre manifesto sintético do MGP9, gate do Pacote 12 ASM/GHR/GV, decisão universitária interna e proveniência sintética.

**Resultado permitido:** `READY_FOR_HUMAN_REVIEW` ou `BLOCKED`; sempre `external_effect=False`.

**Testes:** 5 testes adicionais da ponte; total do sandbox universitário: 14 testes aprovados.

**Limite:** sem integração, rede, gravação externa, publicação, homologação ou efeito jurídico. Próximo gate: revisão humana, pré-registro e autorização explícita.

## Adendo de workflow, segurança e BJI — 2026-08-11

**Implementação adicional:**

- workflow sequencial de pesquisa e extensão, com transições e gates humanos;
- contraditório, voto, fundamentação, revisão, recurso interno e rollback append-only;
- resolução de precedência normativa G6 com bloqueio de empate;
- scanner sintético de segredo/PII, menor privilégio, segregação de tenant, incidentes hash-only e gate `APTO_NO_ESCOPO`;
- `BJI_VALIDATION_SANDBOX_V1/`, com pré-registro e relatório de reprodutibilidade somente de metadados.

**Evidência:** sandbox universitário com 22 testes aprovados; BJI com 5 testes aprovados; estado BJI permanece `NAO_EXECUTADO`.

**Limite:** sem corpus real, execução de modelo, rede, Drive, GitHub, publicação ou efeito externo. Revisão humana e autorização de integração permanecem pendentes.
