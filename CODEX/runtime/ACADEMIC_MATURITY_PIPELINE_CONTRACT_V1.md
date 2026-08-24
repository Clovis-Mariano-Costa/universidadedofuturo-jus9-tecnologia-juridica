# Contrato de pipeline de maturidade acadêmica — V1

**Estado:** `CONTRATO_LOCAL_SANITIZADO / SEM_DADOS_REAIS / SEM_EFEITO_ACADEMICO`

Este pacote implementa apenas guards locais para os estados M00–M23, ensino derivado sanitizado, índice Drive de metadados, manifesto determinístico, papéis e gate de cibersegurança. O índice não copia conteúdo de documentos e não acessa Drive por conta própria.

Regras centrais:

- toda transição precisa de ator, papel registrado, origem, verbo, evidência, estados anterior/posterior, versão, timestamp UTC com cinco casas de milissegundos, classificação, risco, justificativa e rollback;
- estados de aprovação, banca, homologação e publicação exigem `human_gate`;
- publicação exige papel `BIBLIOTECARIO_IA` ou `EDITOR_IA`, evidência de versão/hash, genealogia, sanitização e classificação de acesso;
- `GATE_CYBERSECURITY` é fail-closed: falha crítica, isolamento não testado, autorização incompleta, segredo, rollback ausente, incidente não definido ou integração desconhecida bloqueia;
- material didático é referência sanitizada, não cópia e não verdade canônica; resultados negativos permanecem rotulados;
- não há geração de PDF, nota, banca, homologação, título, colação, publicação real, integração Drive, migração de banco ou deploy;
- nenhuma lei, ato institucional ou competência externa é criada por este código.

## Verificação

```powershell
npm test
```

Fixtures são sintéticas. O pacote não modifica MGP-9 V1/V1.2 e não executa a POC confirmatória de 60 cenários.

## Rollback

Reverter o commit deste contrato e de `academic-maturity-pipeline.mjs`; preservar o recibo e a genealogia. Não há migração nem alteração de dado real.
