# MGP9 POC Sandbox V1

Sandbox local e reprodutível para a implementação mínima do MGP-9. O sandbox usa somente dados sintéticos, não chama serviços externos e não altera rotas existentes da Universidade do Futuro.

## Conteúdo

- `harness.py`: executor pareado dos cenários B11 com as configurações B0–B5.
- `registry.py`: validação dos registros acadêmicos, pesquisa/extensão, dicionários e fontes.
- `data/b11_corpus.json`: corpus sintético versionado.
- `data/configs/b0-b5.json`: configurações versionadas.
- `data/registries/`: exemplos sintéticos com hash SHA-256.
- `schemas/`: contratos mínimos das entidades solicitadas.
- `tests/`: smoke test, execução pareada e validação de registros.
- `docs/CHARLIE_ECHO_MGP9_AULA_V1.md`: material didático governado.

## Execução

Na raiz do repositório:

```powershell
python MGP9_POC_SANDBOX_V1/harness.py --smoke
python MGP9_POC_SANDBOX_V1/harness.py --limit 60
python MGP9_POC_SANDBOX_V1/harness.py
python MGP9_POC_SANDBOX_V1/registry.py validate
python MGP9_POC_SANDBOX_V1/registry.py list --kind dictionary --state SEMENTE
python -m unittest discover -s MGP9_POC_SANDBOX_V1/tests -v
```

Por padrão, o corpus possui 12 cenários e seis configurações, produzindo 72 pares. A opção `--limit 60` preserva também a sequência de 60 resultados brutos prevista no pedido separado do harness. Em ambos os casos, cada resultado bruto permanece individual em `results.jsonl`; nenhum resumo substitui os dados originais.

Cada execução cria um diretório em `MGP9_POC_SANDBOX_V1/artifacts/` contendo:

- `results.jsonl` e `results.csv`;
- `events.jsonl`;
- `manifest.json`;
- `input.sha256` e `output.sha256`;
- `ROLLBACK.md`.

O manifesto registra a versão do corpus, as configurações, a seed, a versão do Python e os hashes. O rollback é recriação/remoção manual do diretório de artefatos identificado; o harness não remove arquivos automaticamente.

## Limites

O executor não é um avaliador jurídico, não consulta fontes oficiais e não produz decisão real. Os registros de Constituição e LGPD são apenas fixtures sintéticos para testar o Authority Registry; qualquer uso acadêmico real exige fonte oficial, data/hora, revisão humana e pré-registro congelado.
