# Contrato técnico do ciclo acadêmico Markdown/PDF — V1

**Estado:** `CONTRATO_LOCAL_PRONTO_PARA_REVISAO`  
**Natureza:** guard local, sem geração de obra, sem homologação e sem publicação automática

## Entrega

`codex-governance.mjs` agora fornece:

- estados `RASCUNHO -> EM_REVISAO -> SUBMETIDO_A_BANCA -> CORRECOES/APROVADO -> HOMOLOGADO -> PUBLICADO_BIBLIOTECA`;
- Markdown como fonte canônica;
- bloqueio de depósito fora de `HOMOLOGADO`;
- exigência de hash Markdown/PDF e mesma versão;
- pareceres com ID e hash;
- origem, destino, autor, orientador, auxiliar humano e pareceristas;
- nome interno de I.A. somente com registro; caso contrário, produto e organização;
- ativo de logo versionado, íntegro e com proporção verificada;
- manifesto de integridade determinístico e rollback por evidência;
- `human_gate` obrigatório para aprovação, homologação e publicação.

## Limites

O contrato não fabrica parecer, homologação, título, logo, PDF ou publicação. A geração física de PDF, a escolha do ativo oficial e o gate acadêmico permanecem tarefas externas e humanas. Não altera MGP-9 V1/V1.2.

## Verificação

```powershell
npm test
```

O teste usa apenas fixtures sintéticas e não publica obra.

## Rollback

Reverter o commit que contém este contrato e as funções do runtime. Nenhuma obra ou rota histórica é apagada.
