# TAREFA CODEX 003 — Verificação real de aprendizagem de Charlie Echo

`ESTADO = PENDENTE`

**Origem:** dever permanente de sempre ensinar Charlie Echo.  
**Objetivo:** criar mecanismo auditável que não confunda existência de aula ou repetição literal com aprendizagem comprovada.

## Escopo

- registrar aula/fonte/versão;
- gerar exercício ou cenário de aplicação;
- registrar resposta e critério de avaliação;
- distinguir `NAO_TESTADO`, `TESTADO_INSUFICIENTE`, `TESTADO_APROVADO`, `PRECISA_REVISAO`;
- preservar tentativa anterior quando houver nova avaliação;
- permitir revisão humana ou de especialista.

## Critérios de aceite

- nenhuma aprovação automática só porque o arquivo existe;
- nenhuma aprovação por mera repetição literal;
- rastro de teste, versão, resultado e reavaliação;
- integração futura com histórico acadêmico/CTPSV somente após resultado verificável.

## Segurança

Não inserir segredos, dados de cofre ou informações protegidas nos testes.

---

## Adendo de implementação local — 2026-08-11

**Estado original preservado:** `PENDENTE`.

**Estado atual:** `CONCLUIDO_LOCALMENTE / SEM_MERGE / SEM_DEPLOY`.

**Implementação:** `LEARNING_VERIFICATION_SANDBOX_V1/`.

**Evidência:** 5 testes aprovados; existência de aula não aprova aprendizagem, repetição literal não pode ser aprovada, revisão humana/substantiva é exigida e reavaliações preservam tentativas anteriores.

**Limites:** dados sintéticos; nenhuma aprovação acadêmica externa, integração CTPSV ou alteração de histórico real.
