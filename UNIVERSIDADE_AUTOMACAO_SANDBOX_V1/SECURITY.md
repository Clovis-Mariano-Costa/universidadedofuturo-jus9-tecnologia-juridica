# Segurança e limites

- dados e testes devem permanecer sintéticos;
- nenhum segredo, token, credencial ou dado pessoal deve entrar no sandbox;
- normas protegidas são somente leitura por padrão;
- alterações exigem nova versão, hash, genealogia e gate humano;
- adjudicação usa exclusivamente `INTERNAL_EXPERIMENTAL`;
- conflito, impedimento, falta de evidência ou efeito externo bloqueiam;
- rollback é append-only e não apaga eventos anteriores;
- nenhuma integração externa é executada automaticamente;
- revisão humana é obrigatória antes de qualquer uso fora do sandbox.
