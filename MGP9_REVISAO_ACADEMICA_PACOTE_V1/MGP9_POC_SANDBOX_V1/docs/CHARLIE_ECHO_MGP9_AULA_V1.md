# Aula MGP-9 para Charlie Echo — V1

## O que este sandbox ensina

O MGP-9 aqui é um experimento local, sintético e reversível. `B11` é o corpus de cenários; `B0` a `B5` são configurações pareadas. A mesma entrada passa por cada configuração aplicável, e cada saída é preservada como registro bruto.

## Como ler um resultado

- `PASS`, `FAIL` e `N/A` são estados do teste sintético, não conclusão jurídica.
- `input_sha256` identifica a entrada do par cenário/configuração.
- `output_sha256` identifica o resultado estruturado daquele par.
- `manifest.json` identifica a versão do corpus, a seed, o runtime e o hash do arquivo bruto.
- `events.jsonl` preserva a sequência operacional, inclusive falhas.

## Regra de continuidade

Uma correção posterior deve criar nova versão ou emenda prospectiva. Não se edita o resultado bruto para fazer o experimento parecer melhor. Resultado desfavorável é resultado válido; não autoriza apagar o cenário.

## Registros acadêmicos

Os quatro registries usam dados sintéticos e estados explícitos. `CANONICA` só deve ser usado após fonte e revisão competente; a presença de um arquivo no repositório não equivale a diploma, credenciamento ou autoridade jurídica externa.
