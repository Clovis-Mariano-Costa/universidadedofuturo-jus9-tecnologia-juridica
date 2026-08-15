# MGP-9 Harness V1.2 — verificação direta

Pacote bruto sanitizado para revisão independente. A V1 e a V1.1 permanecem preservadas em seus diretórios históricos.

## Correções desta versão

- newline canônico `LF` em texto, JSON e CSV gerados;
- serialização JSON determinística: UTF-8, `sort_keys=true`, separadores sem espaços e LF final;
- `is_synthetic=true` obrigatório para `development` e `smoke`;
- `execution_purpose` limitado a `development | smoke | poc_confirmatory`;
- B12 científico rejeita `is_synthetic=true`, ausência de `is_synthetic=false` e qualquer propósito diferente de `poc_confirmatory`;
- execução de 60 cenários bloqueada neste pacote V1.2;
- manifesto, hashes e smoke novos.

## Reprodução autorizada

```powershell
python harness.py --smoke --execution-purpose smoke --output-dir smoke-reproduced
python -m unittest discover -s tests -v
```

O comando `--limit 60` é deliberadamente bloqueado. Nenhuma POC confirmatória foi executada.

## Conteúdo bruto

- `harness.py` — implementação V1.2;
- `b11_corpus.json` — cópia direta do corpus congelado B11;
- `b0-b5.json` — cópia direta das configurações B0–B5;
- `data/` — fontes usadas pelo harness;
- `manifest_sha256_v1_2.txt` — manifesto dos arquivos;
- `smoke/` — saída de 1 par sintético;
- `IMPLEMENTACAO_MGP9_HARNESS_V1_2.md` — relatório técnico;
- `ROLLBACK.md` — procedimento reversível.

## Limite científico

`EXECUCAO_DE_DESENVOLVIMENTO_NAO_EQUIVALE_A_POC_CONFIRMATORIA_PREREGISTRADA.`

Dados sintéticos não são resultados científicos. O harness V1.2 não publica, não faz merge, não faz deploy e não executa a POC confirmatória.
