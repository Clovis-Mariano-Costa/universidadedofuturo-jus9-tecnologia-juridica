# Descoberta e reutilização GAD/UDF

## Baseline lido

Antes da extensão foram lidos o runtime atual e os contratos já entregues nas
PRs 30 e 31: guards de governança, hashes determinísticos, transições
acadêmicas, `human_gate`, rollback, registro de pesquisa e scanner de
marcadores sensíveis. A extensão desta branch não substitui nem duplica esses
contratos; importa seus serializadores e hashes.

## Entrega incremental

- matriz de competência e validação fail-closed, com conflito e autoaprovação bloqueados;
- retenção com `review_at`, checklist de sucessor/impedimento/autoridade e recibo determinístico, sempre sem delete;
- UAAc como evidência objetiva, deduplicada por hash, sem horas, créditos ou título automático;
- linter `acho` que preserva código, citações e diálogo exploratório;
- contrato exato do emblema 1254×1254, SHA-256 e nove dicas;
- manifesto Markdown/PDF/logo/anexos/opiniões/atas/homologação, distinguindo depósito interno e publicação com gate humano.

## Estado

Implementação local em branch de trabalho, com testes unitários offline. Não
foram usados Drive, credenciais, publicação, deploy ou alteração de fontes.
Produção, homologação, publicação, concessão de UAAc e retenção destrutiva
continuam pendentes de seus gates competentes.
