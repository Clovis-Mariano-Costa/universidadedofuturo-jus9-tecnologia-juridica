# Relatório de implementação — Casas, CTPSV/CITAT e automação V1.1

**Data:** 23/08/2026 — America/Sao_Paulo  
**Estado:** `CONCLUIDO_LOCALMENTE / PRONTO_PARA_REVISAO`  
**Natureza:** sandbox offline, sintético, sem efeito externo

## Pedido atendido

Implementação delimitada dos pedidos `PEDIDO_CODEX_AUTOMACAO_TRANSVERSAL_UNIVERSIDADE_CASAS_CTPSV_RPC05_V3_0.md`, `PEDIDO_CODEX_AUTOMACOES_CASAS_CITAT_V2_0.md` e `14_CONTINUIDADE_DUAS_CASAS_E_CODEX_V1_0.md`.

## Entrega

- `houses.py`: inventário somente-leitura, mapa de referências, CITAT autorizado, divergência em quarentena, especialidade auditável, auditoria mensal e relatório operacional;
- `test_houses.py`: 8 testes sintéticos para os contratos novos;
- `CONTRATO_CASAS_CITAT_V1.md`: escopo, limites, verificação e rollback;
- README do sandbox atualizado de forma aditiva.

## Evidência

Comando:

```powershell
python -m unittest discover -s UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/tests -v
```

Resultado observado em 23/08/2026: **30 testes aprovados**. `git diff --check`: aprovado.

Os testes não acessam Drive/GitHub, não sincronizam casas, não movem arquivos, não apagam conteúdo, não usam dados reais e não executam a POC confirmatória do MGP-9.

## Guardas preservados

- Casa-Lar continua fonte documental; Casa-Trabalho continua repertório técnico;
- nenhum documento doméstico, segredo ou credencial é promovido ao GitHub;
- somente campos CITAT explicitamente autorizados, com origem, versão e hash, podem ser propostos;
- divergência produz `QUARANTINED_CONFLICT` e `NO_MOVE_NO_DELETE`;
- `1973-06-16` permanece apenas `marco_simbolico`;
- especialidade não é título: exige caminho, escopo, evidência, revisor e data de revisão;
- auditoria permanece `READ_ONLY` e sem efeito externo.

## Fora do escopo

Integração real com Drive/GitHub, criação automática de pastas, atualização de CITAT real, assinatura humana, publicação, deploy, homologação acadêmica, decisão estatal e exclusão por prazo continuam gates separados.

## Rollback

Reverter o commit desta entrega. A reversão remove somente o contrato novo e a atualização aditiva do README; MGP-9 V1/V1.2, histórico e demais sandboxes permanecem intactos.
