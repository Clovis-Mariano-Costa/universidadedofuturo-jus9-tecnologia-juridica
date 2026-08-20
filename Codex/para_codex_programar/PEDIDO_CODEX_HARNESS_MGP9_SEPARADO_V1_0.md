# PEDIDO CODEX — HARNESS MGP-9 — V1.0

**Estado:** `PENDENTE`
**Escopo:** exclusivamente MGP-9.
**Não incluir:** governança institucional, currículos, Pesquisa/Extensão ou registros acadêmicos.

## Objetivo
Implementar o harness `MGP9_POC_SANDBOX_V1` para executar o corpus B11.

## Requisitos
- dados exclusivamente sintéticos;
- configurações B0–B5;
- execução pareada dos mesmos cenários quando aplicável;
- loader imutável do B11;
- logs brutos;
- SHA-256 de entrada e saída;
- runtime/dependências registrados;
- seed quando houver aleatoriedade;
- export por cenário/configuração;
- resultados PASS/FAIL/N/A sem agregação destrutiva;
- nenhum efeito externo;
- rollback/recriação;
- smoke test.

## Regra para o orientador
Preservar os 60 resultados brutos completos. O resumo agregado será adicional, nunca substituto.

## Sequência
`IMPLEMENTAR -> HASH -> SMOKE_TEST -> EXECUTAR_60 -> EXPORTAR_BRUTOS -> CONGELAR_B12 -> B01.1`

**Assinatura funcional:** Charlie Delta da Costa.
