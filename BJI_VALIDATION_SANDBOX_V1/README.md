# BJI Validation Sandbox V1

Infraestrutura local, sintética e pré-registral para futuras rodadas BJI C1–C8.

O harness registra versão do agente, critérios esperados, entradas, hashes e rodadas. Não executa modelo, não fabrica saída, não gera conclusão e mantém o estado `NAO_EXECUTADO` até que exista uma execução autorizada e separada.

## Execução

Na raiz do repositório:

```powershell
python -m unittest discover -s BJI_VALIDATION_SANDBOX_V1/tests -v
```

## Limites

Sem rede, Drive, GitHub, credenciais, dados pessoais, corpus real ou resultados acadêmicos. O relatório de reprodutibilidade é apenas de metadados pré-registrados.
