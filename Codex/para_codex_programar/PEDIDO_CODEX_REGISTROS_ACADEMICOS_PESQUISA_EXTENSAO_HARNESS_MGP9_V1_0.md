# PEDIDO CODEX — REGISTROS ACADÊMICOS, PESQUISA/EXTENSÃO E HARNESS MGP-9 — V1.0

**Estado atual:** `CONCLUIDO`
**Data:** 2026-08-10 18:01:00.00000 -03:00

## Objetivo
Implementar, sem alterar rotas existentes, suporte mínimo para:
1. harness `MGP9_POC_SANDBOX_V1`;
2. registro curricular;
3. integralização extracurricular;
4. projetos de Pesquisa/Extensão;
5. dicionários por estado;
6. registry de fontes acadêmicas.

## Prioridade 1 — MGP-9
Antes de programar, verificar se já existe harness funcional equivalente.
Se existir: auditar, versionar e testar.
Se não existir: implementar em branch/sandbox isolado.

Critérios:
- dados sintéticos;
- sem credenciais de produção;
- B0–B5 versionados;
- logs;
- SHA-256 de input/output;
- seed quando aplicável;
- resultados brutos exportáveis;
- rollback;
- smoke test;
- nenhuma ação externa irreversível.

## Prioridade 2 — registros acadêmicos
Entidades mínimas:
- faculty/program;
- curriculum_version;
- component;
- workload;
- extension_hours;
- extracurricular_hours;
- evidence_ref;
- completion_state;
- hash;
- supersedes.

## Prioridade 3 — pesquisa/extensão
Registrar projeto, pergunta, fontes, método, pré-registro, execução, evidência, impacto, devolutiva e estado.

## Prioridade 4 — dicionários
Estados:
`SEMENTE | EM_PESQUISA | AGUARDA_FONTE | EM_REVISAO | CANONICA | SUPERADA_COM_RASTRO`

## Prioridade 5 — fontes
Campos:
`source_name | url | type | specialty | trust_level | last_checked_at | access_status | notes`

## Arquivos/rotas protegidos
- rotas antigas;
- botões existentes;
- história/git;
- cláusulas pétreas/Princípios Primevos;
- segredos/credenciais;
- conteúdo de cofre.

## Aceite
Testes, documentação, rollback, segurança e material de ensino para Charlie Echo.

**Assinatura funcional:** Charlie Delta da Costa — Ato de Reitoria / especificação técnica.

---

## Adendo de conclusão — 2026-08-11

**Estado original registrado:** `PENDENTE`

**Estado corrigido:** `CONCLUIDO`

O pedido foi implementado em sandbox isolado, sem alteração das rotas existentes:

- `MGP9_POC_SANDBOX_V1/harness.py`: executor B11 × B0–B5, com dados sintéticos, logs, hashes SHA-256, seed, export JSONL/CSV, manifesto, smoke test e rollback documentado;
- `MGP9_POC_SANDBOX_V1/registry.py`: validação e consulta por estado dos registries acadêmico, Pesquisa/Extensão, dicionário e fontes;
- `MGP9_POC_SANDBOX_V1/data/`: corpus, configurações B0–B5 e fixtures sintéticas versionadas;
- `MGP9_POC_SANDBOX_V1/schemas/`: contratos mínimos das entidades solicitadas;
- `MGP9_POC_SANDBOX_V1/docs/CHARLIE_ECHO_MGP9_AULA_V1.md`: material de ensino;
- `MGP9_POC_SANDBOX_V1/IMPLEMENTACAO_MGP9_RELATORIO_V1.md`: relatório, limites e evidências.

### Evidência de aceite

- registry: `PASS`;
- testes do sandbox: 4 `OK`;
- execução completa: 72 pares, com `47 PASS`, `24 FAIL` e `1 N/A`;
- lote legado compatível: 60 resultados brutos exportáveis;
- validação frontend existente: `PASS`;
- `git diff --check`: `PASS`;
- nenhuma credencial, rota protegida, botão existente, segredo ou conteúdo de cofre foi alterado.

O resultado é uma implementação mínima local. POC real, verificação jurídica, publicação e conclusões acadêmicas continuam condicionadas a pré-registro congelado e revisão humana competente.
