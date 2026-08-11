# Inventário de pedidos de interesse da Universidade do Futuro — 2026-08-11

**Assinatura funcional:** `Atos de Reitoria`  
**Natureza:** etiqueta interna simbólico-operacional; não é assinatura civil/digital nem aprovação humana.

## Portas verificadas

- Fila de pedidos: https://drive.google.com/drive/folders/1SWFZGRpw1CrXakaqfveOB9YjGrmF0im2
- Atos/documentos de Reitoria: https://drive.google.com/drive/folders/13bTWktsLftJqJ4NoeN-aTkrHoefXbcDh
- Quarentena: https://drive.google.com/drive/folders/1a16mk007eGoxDt_GH4YdfaIg9oMMzLIV
- Observação da quarentena: https://drive.google.com/drive/folders/1IfnjfGoaVxdQ3mBQvVaqWnrvUhHb2RjB

As duas pastas foram inventariadas por metadados e leitura dos pedidos diretamente relacionados a registros acadêmicos, pesquisa/extensão, governança, automação e infraestrutura da Universidade. A pasta de material sigiloso da Reitoria não foi aberta nem lida.

## Pedidos executáveis e estado

| Grupo | Estado | Evidência local |
|---|---|---|
| Harness MGP9 separado | concluído localmente, sem merge/deploy | `MGP9_POC_SANDBOX_V1/` |
| Pacote 12 ASM/GHR/GV | concluído localmente, sem merge/deploy | `PACOTE12_ASM_GHR_GV_V1/` |
| Pesquisa/extensão e adjudicação experimental | concluído localmente, sem merge/deploy; interno e não estatal | `UNIVERSIDADE_AUTOMACAO_SANDBOX_V1/` |
| Governança Charlie Echo | concluído localmente, sem merge/deploy | `CHARLIE_ECHO_GOVERNANCA_SANDBOX_V1/` |

Os dois documentos Drive de adjudicação foram tratados como duplicatas/histórico do mesmo pedido; nenhum foi apagado ou sobrescrito.

## Pedidos não concluídos nesta rodada

Pedidos de backend/frontend gerais, pipeline amplo de maturidade, automações transversais, biblioteca/titulação, arquitetura geral e estrutura acadêmica foram classificados como `PENDENTE_ESCopo_ou_GATE_HUMANO`. A execução automática desses itens exigiria definição de escopo, dependências, revisão humana e, em alguns casos, decisão acadêmica ou normativa. Não foram apresentados como concluídos nem enviados à quarentena como se fossem entregas finalizadas.

Atos de Reitoria, regimentos, normas públicas, documentos de banca, requerimentos e registros acadêmicos ativos permanecem fora da quarentena: são documentos normativos, históricos ou sujeitos a homologação humana.

## Protocolo aplicado

- fonte original preservada;
- sem credenciais, dados reais, material sigiloso ou efeito externo;
- sandboxes isolados e sem merge/deploy;
- testes e hashes registrados;
- recibos sanitizados encaminhados somente para a subpasta de observação;
- retenção de 32 dias, com elegibilidade para exclusão em `2026-09-12`, sem exclusão automática por este registro;
- retorno verificável por ID/URL e rastro append-only.

**Resultado:** quatro grupos técnicos foram identificados como concluídos localmente; três recebem novo recibo de quarentena nesta rodada, e o Pacote 12 mantém o recibo já existente.
