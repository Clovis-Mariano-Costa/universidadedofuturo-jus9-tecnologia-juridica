# Registro de execução — MJ9 Inventário Normativo — Fase 1

**Código do pedido:** `PED-CODEX-MJ9-INVENTARIO-2026-08-23-V2.0`  
**Origem Drive:** [pedido](https://docs.google.com/document/d/1qq_-_wdcbjuFZgFe3NAHghy-kzJb4K9BIsmzhd2UskI/edit?usp=drivesdk)  
**Ato de referência:** [ATO-ORG-MJ9-2026-08-23-V1.0](https://docs.google.com/document/d/1fGFwGxglxxrnwR05eWMgBp6uN473JyOC35W0nIEqMRc/edit?usp=drivesdk)  
**Registro Mestre:** [REG-MESTRE-MJ9-2026-08-23-V1.0](https://docs.google.com/document/d/1RsiEWZcWWcCsMKd7QnOlk2_iZ1DiFHy048UyO1LVvNA/edit?usp=drivesdk)  
**Data real:** 2026-08-23  
**Estado:** `FASE1_IMPLEMENTADA_LOCALMENTE / PR_DRAFT / NAO_MESCLADO`

## Implementação

Criado `tools/normative_inventory/` com:

- inventário determinístico a partir de fixtures de metadados Drive/GitHub;
- normalização UTF-8/LF e hash SHA-256 quando bytes estão disponíveis;
- duplicatas exatas por hash e prováveis por nome/tamanho/MIME, sempre preservando originais;
- classificação como candidato, sem declarar vigência por nome;
- estado desconhecido como `SEM ESTADO CONFIRMADO`;
- matriz normativa, JSON, CSV, Markdown e histórico incremental;
- identificação de conteúdo potencialmente sensível sem reproduzir nome/path no relatório saneado;
- bloqueio explícito de `--write`.

## Verificação

- testes locais: 7 aprovados;
- regressão do runtime existente: 15 testes Node aprovados;
- smoke CLI: executado em modo `DRY_RUN_READ_ONLY`;
- hash do relatório de fixture: `5e0d18385e489cd64ebdfe95a3785b7f113df7ae918b3008e4e5b32679541ed2`;
- nenhuma credencial, token, conteúdo real ou escrita em Drive/GitHub.

## Limites

Esta entrega ainda não é a reconciliação completa CA02–CA08. Não houve leitura recursiva ao vivo das raízes Drive/GitHub, não foram usados os 310 arquivos/286 hashes como resultado desta execução e não houve integração com Apps Script, publicação, merge ou alteração de fontes. O grupo de dezessete Juramentos e demais critérios de aceitação permanecem pendentes de fixtures/exportações autorizadas e revisão do Legislador.

## Rollback

Fechar o PR draft e remover somente os arquivos adicionados pela branch. Nenhuma fonte externa foi alterada.
