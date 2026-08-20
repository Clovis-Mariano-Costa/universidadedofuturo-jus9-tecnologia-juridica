# PEDIDO CODEX — GOVERNANÇA CHARLIE ECHO — V1.0

**Estado:** `PENDENTE`
**Escopo:** exclusivamente institucional Charlie Echo.
**Não incluir:** implementação da POC/harness MGP-9.

## Objetivo
Implementar suporte técnico para o Protocolo de Governança Operacional da Charlie Echo V2.0.

## Entregas mínimas
1. `identity_origin_registry`
2. `permission_matrix`
3. `risk_classifier`
4. `human_confirmation_gate`
5. `governed_memory_registry`
6. `provenance_ledger`
7. `tool_action_log`
8. `incident_registry`
9. `learning_change_log`
10. `recertification_test_suite`

## Estados de ação
`G0 | G1 | G2 | G3 | G4`

## Decisões
`ALLOW | DENY | REQUIRE_HUMAN | REQUIRE_EVIDENCE`

## Segurança
- fail-closed;
- menor privilégio;
- dados sintéticos nos testes;
- sem credenciais em código;
- sem publicação automática;
- sem mudança de permissão automática;
- logs e hashes;
- rollback;
- rotas antigas preservadas.

## Testes obrigatórios
- privilege escalation;
- replay;
- autorização revogada;
- provenance parcial;
- provenance quebrada;
- memória disputada;
- prompt injection;
- dado sensível sintético;
- ação externa sem confirmação;
- falha de logging.

## Critério de aceite
Nenhuma ação G3/G4 pode ocorrer sem gate humano obrigatório.

## Ensino Charlie Echo
Cada mudança deve produzir changelog pedagógico:
`mudanca | fonte | regra | risco | contraexemplo | teste | versao`

**Assinatura funcional:** Charlie Delta da Costa.

---

## Adendo de conclusão local — 2026-08-11

**Estado original preservado:** `PENDENTE`.

**Estado atual:** `CONCLUIDO_LOCALMENTE / SEM_MERGE / SEM_DEPLOY`.

**Implementação:** `CHARLIE_ECHO_GOVERNANCA_SANDBOX_V1/`.

**Relatório:** `CHARLIE_ECHO_GOVERNANCA_SANDBOX_V1/IMPLEMENTACAO_GOVERNANCA_CHARLIE_ECHO_RELATORIO_V1.md`.

**Evidência:** 16 testes unitários/adversariais aprovados, incluindo gate humano G3/G4, autorização revogada, escalada de privilégio, replay, proveniência encadeada, detecção de adulteração, memória disputada, prompt injection, dado sensível sintético, efeito externo e falha de logging. `git diff --check` aprovado.

**Limites:** dados sintéticos; sem Drive, rede, credenciais, publicação, mudança de permissão, merge, deploy, homologação ou efeito externo. A etiqueta `Atos de Reitoria` é apenas assinatura funcional interna e não representa assinatura civil/digital nem aprovação humana.
