# Contrato offline de Casas, CTPSV/CITAT e automação — V1

**Estado:** `SANDBOX_READY_FOR_REVIEW`  
**Natureza:** contrato local, sintético e sem efeito externo  
**Pedido relacionado:** `PEDIDO_CODEX_AUTOMACAO_TRANSVERSAL_UNIVERSIDADE_CASAS_CTPSV_RPC05_V3_0.md` e `PEDIDO_CODEX_AUTOMACOES_CASAS_CITAT_V2_0.md`

## Implementação

`houses.py` implementa:

- inventário determinístico e somente-leitura de `membro -> Casa-Lar -> Casa-Trabalho -> CITAT -> especialidades -> automações`;
- bloqueio de segredo, PII e conteúdo doméstico no metadado recebido;
- sincronização somente de campos CITAT explicitamente autorizados, com origem, versão e hash;
- divergência de hash em `QUARANTINED_CONFLICT`, sem mover, apagar ou sobrescrever conteúdo;
- duas vias de especialização (`university_training` e `documented_work`), ambas exigindo escopo, evidência, revisor e revisão futura;
- auditoria mensal `READ_ONLY`, com hash por registro e hash do relatório;
- relatório operacional com finalidade, acesso, riscos, responsável e rollback;
- `1973-06-16` apenas como `marco_simbolico`; datas de criação, assinatura, atualização e revisão devem ser reais.

## Não implementado por desenho

Não há conector Drive/GitHub, criação automática de pastas, atualização de CITAT real, assinatura humana, exclusão, publicação, deploy, decisão estatal, título acadêmico ou sincronização de documentos domésticos. Esses efeitos exigem revisão e autorização específicas fora do sandbox.

## Verificação

```powershell
python -m unittest discover -s UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/tests -v
```

O teste usa apenas fixtures sintéticas. O MGP-9 V1/V1.2 não é importado nem executado por este contrato.

## Rollback

Reverter o commit desta entrega ou remover `houses.py`, `test_houses.py` e este contrato. Nenhum arquivo histórico ou dado externo é alterado pelo módulo.
