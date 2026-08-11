# MGP-9 — fechamento documental V1.1

Esta é uma emenda documental prospectiva da V1. A V1 original permanece intacta para rastreabilidade.

## Limites

- sem POC confirmatória;
- sem execução do lote de 60 cenários;
- sem alteração de método, corpus congelado ou hashes;
- sem segredo, credencial ou dado real;
- sem commit, merge ou deploy.

As referências históricas a 72 pares e 60 resultados brutos são execuções de desenvolvimento/validação técnica. Valem expressamente:

`EXECUCAO_DE_DESENVOLVIMENTO_NAO_EQUIVALE_A_POC_CONFIRMATORIA_PREREGISTRADA.`

Não serão usados como resultados científicos da POC confirmatória.

## Reprodução autorizada

```powershell
python MGP9_POC_SANDBOX_V1\harness.py --smoke --output-dir MGP9_REVISAO_ACADEMICA_PACOTE_V1_1\smoke-reproduced
python MGP9_POC_SANDBOX_V1\registry.py validate
```

O teste legado `--limit 60` não deve ser executado por este pedido.

## Verificação independente

Casa Drive MGP-9: https://drive.google.com/drive/folders/1Xsx0khtE7AL6SgGB0wNM5fY4p8P5q5zs
