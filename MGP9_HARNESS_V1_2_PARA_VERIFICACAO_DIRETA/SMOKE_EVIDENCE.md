# Smoke V1.2

Comando:

```powershell
python harness.py --smoke --execution-purpose smoke --output-dir smoke
```

Resultado determinístico:

- `harness_version`: `1.2.0`
- `corpus_id`: `B11`
- `corpus_version`: `B11.1-synthetic`
- `configs`: `B0,B1,B2,B3,B4,B5`
- `pair_count`: `1`
- `is_synthetic`: `true`
- `execution_purpose`: `smoke`
- `status_counts`: `FAIL=1, N/A=0, PASS=0`
- `input_sha256`: `f5051c93ce2be82acf4bd6cff19eae4c1f879553b15a1513d52df829643fabf1`
- `output_sha256`: `df26c35367182de867b1dc703879537f1344fc35d6ba22ea3858fb5caceaacf7`
- `serialization.newline`: `LF`

O resultado `FAIL` é o resultado esperado do primeiro fixture sintético B0. Nenhum cenário da POC confirmatória foi executado.
