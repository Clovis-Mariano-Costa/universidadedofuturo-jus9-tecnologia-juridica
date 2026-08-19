# Runtime auditável da Casa CODEX — pacote técnico V1

Este pacote implementa apenas funções locais, determinísticas e sem integração externa para os pedidos CODEX 002, 003 e 004, além dos guards necessários à governança de execução do MGP-9 e da adjudicação experimental.

## O que foi implementado

- normalização de newline para LF e serialização determinística por chaves ordenadas;
- validação de `execution_purpose` e `is_synthetic`;
- bloqueio de dados sintéticos ou não confirmatórios na porta B12;
- trava preventiva para pedidos visuais destinados a representar PAI AMOR;
- registro de aula, tentativa, revisão humana e estados de aprendizagem;
- infraestrutura de rodada BJI iniciando em `NAO_EXECUTADO`, sem resultados ou conclusão pré-preenchidos;
- guard de imutabilidade para normas protegidas;
- registro experimental explicitamente não estatal e dependente de `human_gate` para efeito externo.
- transições acadêmicas com evidência obrigatória;
- validação estrutural de casos experimentais;
- manifesto de rollback e scanner de marcadores sensíveis sem expor valores.

## Verificação

Na pasta `CODEX/runtime`:

```text
npm test
```

O teste não gera imagens, não executa a POC MGP-9, não usa corpus real e não publica nada.

## Limites

Este é um núcleo local de validação. Ele não substitui integração com Drive/GitHub, banco de dados, RBAC/ABAC, pipeline de deploy, revisão humana, pré-registro ou execução empírica. O MGP-9 V1/V1.2 e seu corpus permanecem preservados e separados.

## Rollback

Remover os arquivos deste diretório e reverter o commit desta branch. Nenhuma rota pública ou arquivo histórico é alterado por este pacote.
