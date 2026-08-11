# TAREFA CODEX 004 — Infraestrutura auditável para pesquisa BJI C1–C8

`ESTADO = PENDENTE`

**Origem:** Projeto de Pesquisa BJI e protocolo de validação C1–C8.  
**Objetivo:** preparar infraestrutura técnica para futura pesquisa empírica sem fabricar resultados.

## Escopo

- separar corpus, entradas, saídas, configurações e resultados;
- registrar versão do agente/modelo quando disponível;
- registrar critério esperado antes da avaliação;
- preservar logs sanitizados e hashes quando aplicável;
- permitir revisão independente;
- diferenciar validação documental de teste empírico;
- produzir relatório reprodutível por rodada.

## Critérios de aceite

- zero resultado pré-preenchido;
- entradas e saídas rastreáveis;
- estado `NAO_EXECUTADO` enquanto experimento não ocorrer;
- versões e critérios preservados;
- nenhuma conclusão acadêmica automática gerada pela infraestrutura.

## Ensino Charlie Echo

O conhecimento técnico gerado deve ser convertido em material de aula sobre evidência, experimento, versão, falsificabilidade e limites.

---

## Adendo de implementação local — 2026-08-11

**Estado original preservado:** `PENDENTE`.

**Estado atual:** `CONCLUIDO_LOCALMENTE / NAO_EXECUTADO / SEM_MERGE / SEM_DEPLOY`.

**Implementação:** `BJI_VALIDATION_SANDBOX_V1/`.

**Evidência:** 5 testes aprovados; pré-registro exige critérios anteriores à avaliação, impede resultados/conclusões pré-preenchidos, registra hashes de entrada e produz relatório somente de metadados.

**Limites:** nenhum agente/modelo foi executado e nenhuma conclusão acadêmica foi criada.
