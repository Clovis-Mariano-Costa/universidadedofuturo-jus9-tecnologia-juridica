# MGP-9 — fechamento documental do harness V1

## Estado

- Sandbox preservado: `MGP9_POC_SANDBOX_V1/`.
- Sem branch nova, commit, merge ou deploy nesta rodada; o worktree já contém alterações locais de outros pedidos.
- Pacote sanitizado para revisão acadêmica independente.
- Nenhum segredo, credencial ou dado real incluído.
- A POC confirmatória de 60 cenários não foi executada neste fechamento.

## Reprodução segura

Na raiz do repositório:

```powershell
python MGP9_POC_SANDBOX_V1\harness.py --smoke --output-dir MGP9_REVISAO_ACADEMICA_PACOTE_V1\smoke-reproduced
python MGP9_POC_SANDBOX_V1\registry.py validate
python -m unittest discover -s MGP9_POC_SANDBOX_V1/tests -v
```

O último comando contém um teste legado que executa o lote de 60 pares; por causa deste pedido, ele foi preservado no código, mas foi marcado como `SKIPPED_BY_CLOSING_REQUEST` na saída documental deste pacote. O fechamento executou apenas o smoke test, a validação do loader/registries e os demais testes sintéticos autorizados.

## Conteúdo

- `MGP9_POC_SANDBOX_V1/`: cópia sanitizada do sandbox para verificação independente.
- `TREE_SANDBOX.txt`: árvore dos arquivos.
- `MANIFEST_SHA256_MGP9_V1.txt`: hashes SHA-256 do pacote, excluindo o próprio manifesto.
- `TESTES_4_SAIDA_INTEGRAL.txt`: saída integral dos quatro testes, com o teste de 60 pares explicitamente pulado.
- `SMOKE_EVIDENCE.txt`: evidência do único smoke test executado.
- `B0_B5_DESCRICAO.md`: descrição das configurações B0–B5.
- `LOADER_CORPUS_EVIDENCE.md`: evidência do loader, corpus sintético e registries.
- `EXPORT_BRUTO_EXAMPLE.jsonl`: exemplo sintético de exportação bruta.
- `ROLLBACK_PROCEDURE.md`: procedimento de rollback sem remoção automática.

## Retorno para Charlie Delta

Casa Drive do MGP-9: https://drive.google.com/drive/folders/1Xsx0khtE7AL6SgGB0wNM5fY4p8P5q5zs  
Pacote Drive: será informado somente após a criação e a leitura de verificação do subdiretório.
