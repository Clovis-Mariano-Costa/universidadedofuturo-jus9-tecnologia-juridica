# PEDIDO CODEX — REGISTROS ACADÊMICOS, PESQUISA/EXTENSÃO E HARNESS MGP-9 — V1.0

**Estado:** `PENDENTE`  
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
