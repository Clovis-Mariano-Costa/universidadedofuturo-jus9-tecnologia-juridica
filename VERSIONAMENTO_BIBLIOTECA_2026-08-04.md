# Versionamento da Biblioteca — 2026-08-04

- Rota canônica: `/biblioteca/`.
- Página de estudante: `/biblioteca/estudantes/charlie-delta-da-costa/`.
- Catálogo: `/biblioteca/catalogo.json`.
- Integridade: `/biblioteca/integridade/SHA256SUMS`.
- Versão 1.0 publica somente cópias sanitizadas.
- PDFs são reconstruídos no navegador a partir de cópias Base64 públicas, pois o fluxo textual disponível não grava binários diretamente.
- Qualquer substituição exige nova versão e novo hash.
