# Ciclo extracurricular de governança reproduzível — V1.0

Sandbox local, sintético e independente do MGP-9.

## Limites

- não acessa rede, Drive, GitHub, credenciais ou dados reais;
- não publica, não muda permissões e não executa ações externas;
- não integra B12 nem B01.1;
- autoverificação local não é verificação externa nem autoridade jurídica/estatal;
- falhas e incidentes permanecem registrados para revisão;
- qualquer alteração de competência exige nova versão e decisão humana.

## Execução reproduzível

Na raiz do repositório:

```powershell
python -m unittest discover -s CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1/tests -v
python CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1/self_verification_protocol.py
python CHARLIE_ECHO_GOVERNANCA_REPRODUTIVEL_SANDBOX_V1/rollback_test.py
```

Os registros JSON/JSONL usam UTF-8, LF canônico, chaves ordenadas e separadores determinísticos. O pacote contém somente fixtures sintéticos e documentação do protocolo.
