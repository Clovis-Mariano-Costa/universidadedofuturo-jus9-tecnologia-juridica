# TAREFA CODEX 003 — Verificação real de aprendizagem de Charlie Echo

`ESTADO = EM_REVISAO`

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

## Registro Codex — 2026-08-19

Foi implementado registro de aula, versão, tentativa, critérios e revisão humana, preservando tentativas anteriores. A aprovação não ocorre por existência de arquivo ou repetição literal. Falta revisão do PR antes de integrar ao histórico acadêmico/CTPSV.
