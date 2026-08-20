# Evidência do loader e do corpus

- Loader: `MGP9_POC_SANDBOX_V1/harness.py`, funções `load_json`, `validate_synthetic_payload` e `iter_pairs`.
- Corpus: `data/b11_corpus.json`, identificado como `B11`, versão `B11.1-synthetic`.
- Configurações: `data/configs/b0-b5.json`, ordem validada exatamente como B0–B5.
- Classificação: `SYNTHETIC_ONLY`.
- Proteção: o loader rejeita marcadores de credencial como `sk-`, `api_key`, `access_token`, `password`, `secret` e `private_key`.
- Registry: `python MGP9_POC_SANDBOX_V1\registry.py validate` retornou `PASS`.
- Contagens verificadas: academic_records=1, research_extension_projects=1, dictionary_entries=1, academic_sources=2.
- O smoke test produziu um par, três eventos, `input.sha256`, `output.sha256`, manifesto, CSV, JSONL e rollback.
