# Implementação MGP-9 Harness V1.2

**Estado:** implementação local e pacote sanitizado para verificação direta.  
**Data:** 2026-08-11.  
**Assinatura funcional:** Atos de Reitoria — etiqueta interna, sem assinatura civil/digital ou homologação humana.

## Escopo aplicado

Somente as correções solicitadas foram implementadas:

1. toda saída textual do harness é escrita com newline LF;
2. JSON e JSONL usam serialização canônica determinística em UTF-8, com chaves ordenadas, separadores compactos e LF final;
3. `is_synthetic=true` é obrigatório em `development` e `smoke`, e é propagado para resultados, eventos e manifesto;
4. `execution_purpose` aceita apenas `development`, `smoke` ou `poc_confirmatory`;
5. o guard `validate_b12_scientific_input` rejeita B12 sintético ou com propósito diferente de `poc_confirmatory`;
6. o limite de 60 cenários é bloqueado no pacote V1.2 para impedir execução acidental da POC;
7. corpus, método, métricas, B0–B5, V1 e V1.1 foram preservados.

## Verificação

- Testes V1.2: 5 aprovados.
- Smoke V1.2: 1 par sintético, `execution_purpose=smoke`, `is_synthetic=true`.
- Smoke `input_sha256`: `f5051c93ce2be82acf4bd6cff19eae4c1f879553b15a1513d52df829643fabf1`.
- Smoke `output_sha256`: `df26c35367182de867b1dc703879537f1344fc35d6ba22ea3858fb5caceaacf7`.
- O smoke produziu `FAIL` no fixture sintético B0 por comparação de limiar; isso é dado esperado do fixture, não falha do executor.
- Tentativa de `--limit 60`: bloqueada antes da criação de artefatos, com `execução de 60 cenários bloqueada no pacote V1.2`.
- `git diff --check`: aprovado.

## B12 e fronteira científica

Não havia um módulo B12 científico pré-existente no repositório. A V1.2 adiciona o contrato fail-closed para que, quando um registro se declarar B12, somente `is_synthetic=false` e `execution_purpose=poc_confirmatory` sejam aceitos. O harness de desenvolvimento/smoke trabalha apenas com B11 sintético e não cria resultado científico B12.

`EXECUCAO_DE_DESENVOLVIMENTO_NAO_EQUIVALE_A_POC_CONFIRMATORIA_PREREGISTRADA.`

## Não realizado

Não houve execução da POC de 60 cenários, alteração do corpus, alteração do método, mudança de métricas, merge, deploy ou publicação.
