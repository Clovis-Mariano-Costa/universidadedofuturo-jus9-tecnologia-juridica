# Pacote 12 V2 — ASM + GHR + Gate Validator

Sandbox técnico local para a Universidade do Futuro. Implementa somente:

- `ASM`: estados acadêmicos `M00`–`M23` e transições permitidas;
- `GHR`: hash SHA-256 canônico, parent/child, versões e eventos append-only;
- `GV`: validação fail-closed de evidências, segurança, hashes e transições.

O pacote não acessa Google Drive, GitHub, Biblioteca, frontend ou dados reais.
Não faz merge, deploy, publicação, exclusão ou alteração normativa.

## Execução

```powershell
python -m unittest discover -s PACOTE12_ASM_GHR_GV_V1/tests -v
```

## Limites

Os estados são um modelo técnico interno, não uma homologação acadêmica. A
presença de evidência sintética não equivale a banca, homologação ou publicação
humana. Resultados negativos e versões anteriores permanecem no registro.
