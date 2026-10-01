# Evidência de rollback

O teste `rollback_test.py` cria um estado sintético, salva um snapshot, aplica uma alteração, restaura o snapshot e compara os hashes SHA-256.

Resultado observado nesta versão: `passed=True`.

- baseline: `fd0a616758e83597cf47f587f81567830ca1b92182e2e61560fefad21cc06465`
- alterado: `15783a0ae76c79a74495a5f33704a54859524767f705eba38a663b87e242bb3b`
- restaurado: `fd0a616758e83597cf47f587f81567830ca1b92182e2e61560fefad21cc06465`

Nenhum arquivo externo é removido automaticamente.
