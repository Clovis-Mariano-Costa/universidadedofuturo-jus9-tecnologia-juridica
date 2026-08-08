# PEDIDO CODEX — PACOTE 12 V2.0 — ASM + GHR + GATE VALIDATOR — V1.0

## Escopo técnico estrito
Implementar somente:
1. Academic State Machine (ASM);
2. Genealogy & Hash Record (GHR);
3. Gate Validator (GV).

## Não implementar nesta rodada
Biblioteca completa; CTPSV/CITAT; dicionários; ensino automatizado a Charlie Echo; adjudicação experimental; frontend completo; backend geral da Universidade; titulação automática; memória governada do Pacote 99.

## Requisitos
- estados acadêmicos versionados;
- transições permitidas/proibidas;
- SHA-256 do objeto canônico;
- genealogia pai/filho;
- bloqueio fail-closed;
- motivo de bloqueio legível;
- rollback preservando histórico;
- resultados negativos preservados;
- evento: origem -> regra -> transformação -> destino -> versão -> hash -> ator -> resultado -> rollback;
- testes unitários, integração, adversariais e regressão;
- sem remoção de rotas existentes;
- sem segredos em logs.

## Casos de aceite
Hash divergente entre avaliadores; depósito precoce; homologação sem evidência; alteração sem nova versão; rollback; estado terminal forçado; caso válido sem falso bloqueio.

## Métricas
TTI, DOND, TBC e TFB conforme Projeto de Pesquisa Pacote 12 V2.0.

## Stop criteria técnicos
Se a implementação exigir Biblioteca, CTPSV, dicionários ou redesign amplo da plataforma, PARAR e reportar dependência; não ampliar escopo automaticamente.

## Casas canônicas de programação
- GitHub: `Codex/para_codex_programar`
- Drive: `https://drive.google.com/drive/folders/1SWFZGRpw1CrXakaqfveOB9YjGrmF0im2`

## Preservação
Não tocar em cláusulas pétreas, Princípios Primevos/Quânticos ou documentos classificados como somente leitura. Mudanças de software não alteram norma acadêmica por implicação.

**Assinatura funcional de especificação:** Charlie Delta da Costa.
