# Segurança do sandbox

- O corpus e os fixtures são sintéticos e não contêm credenciais de produção.
- O harness não usa rede, ambiente autenticado, banco externo ou ação transacional.
- URLs nos fixtures de fontes são referências documentais; `NOT_CHECKED_SYNTHETIC_FIXTURE` impede tratá-las como verificação jurídica executada.
- `registry.py list` é somente leitura; a fonte JSON não é modificada pela consulta.
- Artefatos de execução ficam em diretório próprio e o rollback é manual, identificado e limitado ao sandbox.
- Se um segredo real for encontrado, a execução deve parar e o conteúdo não deve ser publicado.
