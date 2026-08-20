# Relatório de implementação MGP-9 — V1

## Registro da rodada

- Pedido de origem: `CODEX/para_codex_programar/PEDIDO_CODEX_REGISTROS_ACADEMICOS_PESQUISA_EXTENSAO_HARNESS_MGP9_V1_0.md`.
- Orientação consultada: `PARA_ORIENTADOR_MGP9_PRE_REGISTRO_E_IMPLEMENTACAO_MINIMA_V1_0` na pasta de orientações do Drive.
- Auditoria inicial: não foi localizado harness executável equivalente; havia pedidos e documentos de governança, mas nenhum executor funcional.
- Estratégia: sandbox novo, sem alteração de rotas existentes e sem integração externa.

## Entregue

1. Harness pareado B11 × B0–B5, com dados sintéticos, seed registrada, logs, SHA-256 de entradas e saídas, export JSONL/CSV, manifesto, smoke test e plano de rollback.
2. Modelos mínimos para `faculty`, `program`, `curriculum_version`, `component`, `workload`, `extension_hours`, `extracurricular_hours`, `evidence_ref`, `completion_state`, `hash` e `supersedes`.
3. Registro de Pesquisa/Extensão com pergunta, fontes, método, pré-registro, execução, evidência, impacto, devolutiva e estado.
4. Dicionário com os estados `SEMENTE`, `EM_PESQUISA`, `AGUARDA_FONTE`, `EM_REVISAO`, `CANONICA` e `SUPERADA_COM_RASTRO`.
5. Registry de fontes com os campos solicitados e fixtures sintéticas de Constituição e LGPD, marcadas como não verificadas para uso real.
6. Material didático para Charlie Echo, preservando resultado negativo, hipótese e limites epistemológicos.

## Evidência de teste

- `python MGP9_POC_SANDBOX_V1/registry.py validate`: PASS.
- `python -m unittest discover -s MGP9_POC_SANDBOX_V1/tests -v`: 4 testes, OK.
- Execução completa: 72 pares, `47 PASS`, `24 FAIL`, `1 N/A`.
- Execução compatível com o pedido separado: 60 resultados brutos preservados.
- `node tests/validate-frontend.mjs`: PASS; rotas existentes preservadas.
- `git diff --check`: PASS.

## Limites e próximo gate

Este resultado implementa a camada mínima local. Não executa POC-72 em fonte real, não verifica vigência jurídica, não publica, não acessa credenciais e não substitui o congelamento metodológico, a revisão do orientador ou a revisão humana. Qualquer mudança após hash deve ser uma emenda prospectiva versionada.
