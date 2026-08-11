# Teaching package — Pacote 12 V2

**Fonte:** `core.py` e `tests/test_package12.py`  
**Versão:** V1  
**Estado:** MATERIAL_DIDATICO_INTERNO  
**Risco:** confundir validação técnica sintética com aprovação acadêmica real  
**Revisão humana necessária:** sim

## Conceito

ASM decide se uma transição de estado é estruturalmente possível; GHR preserva
hash, versão, parent/child e o evento de transformação; GV decide se a
transição tem evidência suficiente e bloqueia por padrão quando falta prova.

## Contraexemplo

Um recibo de publicação sem `same_version_hash` não é suficiente. O sistema
deve bloquear, mesmo que o título e o estado pareçam corretos.

## Teste esperado

Hash divergente entre avaliadores retorna `HASH_DIVERGENCE`; rollback retorna
`ROLLBACK_APPLIED` em uma nova versão, sem apagar as versões anteriores.

## Limite

O pacote não verifica a autenticidade de uma banca ou documento externo; ele
verifica a presença e a coerência dos metadados fornecidos ao sandbox.
