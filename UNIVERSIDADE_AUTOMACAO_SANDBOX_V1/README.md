# Universidade Automação Sandbox V1

Sandbox offline e segregado para o pedido `PEDIDO_CODEX_UNIVERSIDADE_PESQUISA_EXTENSAO_ADJUDICACAO_V1_0.md`.

## Implementado

- registro versionado de normas com hash e proteção `READ_ONLY_BY_DEFAULT`;
- fluxo explícito de atualização protegida com `human_gate` e `constitutional_flow`;
- registry mínimo de pesquisa/extensão com estado, fontes, pré-registro, execução, evidência, impacto, devolutiva e hash;
- adjudicação experimental com jurisdição interna, conflito, evidência, revisão, gate humano e rollback append-only;
- quarentena de fonte sem identificador verificável;
- linter de status, hash protegido, referência quebrada e falsa autoridade externa;
- eventos de proveniência encadeados por SHA-256;
- ponte dry-run somente leitura entre MGP9, Pacote 12 ASM/GHR/GV e decisão universitária interna;
- workflow sequencial de pesquisa e extensão com gates humanos;
- contraditório, votos, fundamentação, revisão e recurso interno na adjudicação;
- regra de precedência normativa G6 com bloqueio de empate;
- scanner sintético de segredo/PII, segregação de tenant, menor privilégio e gate `APTO_NO_ESCOPO`;
- testes adversariais e dados sintéticos.
- contrato offline de Casas-Lar/Casas-Trabalho/CITAT: inventário somente-leitura, mapa de referências, sincronização restrita, divergência em quarentena, especialização com evidência/revisor/validade e auditoria mensal determinística;
- separação explícita de marco simbólico (`1973-06-16`) e datas reais de criação, assinatura e atualização.

## Execução

Na raiz do repositório:

```powershell
python -m unittest discover -s UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/tests -v
```

## Limites

O sandbox não acessa Drive, GitHub, normas reais, credenciais, dados pessoais, Poder Judiciário, MEC ou qualquer serviço externo. Não cria jurisdição, sanção, título, homologação, publicação ou efeito jurídico. A presença de uma decisão interna não equivale a decisão estatal.

## Casas e CITAT

`houses.py` aceita somente metadados fornecidos pelo chamador. O inventário não baixa nem copia conteúdo da Casa-Lar. A sincronização só pode propor campos CITAT autorizados e com origem, versão e hash; divergências produzem `QUARANTINED_CONFLICT` com `NO_MOVE_NO_DELETE`. A auditoria é `READ_ONLY` e toda alteração externa permanece fora deste sandbox.

## Ponte dry-run

`bridge.py` compõe, em memória, um manifesto sintético do MGP9, um gate do Pacote 12, uma decisão universitária interna e um registro de proveniência. O resultado possível é somente `READY_FOR_HUMAN_REVIEW` ou `BLOCKED`; a ponte nunca retorna aprovação, publicação ou efeito externo.

`SecurityGate` produz `APTO_NO_ESCOPO` apenas para dados sintéticos sem achados, escopo segregado e menor privilégio compatível. Achados sensíveis abrem incidente com hash, sem registrar o valor.

## Próximo gate

Revisão humana do contrato da ponte e dos workflows, definição de pré-registro e autorização explícita antes de qualquer integração ou uso em corpus real.
