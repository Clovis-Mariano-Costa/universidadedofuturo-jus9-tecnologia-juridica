# Procedimento de rollback

1. Confirmar o caminho exato do artefato ou do subdiretório criado.
2. Preservar o manifesto, hashes e registro de revisão antes de qualquer remoção.
3. Remover manualmente somente o diretório de artefatos da execução, nunca o sandbox nem o corpus.
4. Recriar o smoke test em um diretório novo com o comando do README.
5. Registrar a diferença e a nova versão; não sobrescrever histórico.

O harness não remove arquivos automaticamente e não altera dados fora de `MGP9_POC_SANDBOX_V1/artifacts/` ou do diretório explicitamente escolhido para a execução.
