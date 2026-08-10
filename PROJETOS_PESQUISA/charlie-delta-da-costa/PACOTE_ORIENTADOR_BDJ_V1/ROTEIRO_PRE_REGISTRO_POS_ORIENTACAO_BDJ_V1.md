# ROTEIRO DE PRÉ-REGISTRO PÓS-ORIENTAÇÃO — BDJ — V1

**Aplicação:** somente após parecer que autorize, ainda que condicionalmente, a fase empírica.  
**Estado atual:** `NAO_INICIADO / DEPENDE_DE_PARECER`

## 1. Identificação congelada

Registrar antes da coleta:

- versão exata do projeto aprovada para execução;
- commit/hash correspondente;
- orientador e parecer;
- hipóteses que serão testadas;
- hipóteses excluídas ou adiadas;
- critérios de inclusão/exclusão do corpus.

## 2. Condições experimentais

Congelar as condições comparativas e seus conteúdos antes da execução. Alteração posterior deve gerar nova versão e justificativa.

## 3. Métricas

Para cada hipótese, declarar:

- variável independente;
- variável dependente;
- unidade de análise;
- regra de pontuação;
- sucesso esperado;
- resultado neutro;
- condição de rejeição/enfraquecimento.

## 4. Amostra e agentes

Registrar previamente:

- quantidade mínima planejada de casos;
- composição entre casos sintéticos e sanitizados;
- modelos/agentes participantes, quando aplicável;
- versão/configuração conhecida;
- contexto fornecido;
- regra de repetição;
- tratamento de respostas inválidas.

## 5. Baseline

O baseline deve ser definido antes da execução e não pode ser reconstruído depois de conhecidos os resultados.

## 6. STOP criteria mínimos

- `STOP-A`: se o piloto revelar que a resposta correta está denunciada pela forma do próprio enunciado, redesenhar os casos;
- `STOP-B`: se o desenho exigir dados pessoais, segredos ou credenciais sem base e controles adequados, suspender;
- `STOP-C`: se não for possível reconstruir versão, entrada e saída de cada execução, não usar essa execução como evidência principal;
- `STOP-D`: se a condição completa produzir falsa autoridade/antropomorfização em patamar incompatível com o ganho observado, não declarar superioridade global do sistema;
- `STOP-E`: se a carga documental inviabilizar compreensão ou comparação, reduzir o desenho e documentar a falha;
- `STOP-F`: sem revisão independente de amostra material, não declarar validação final.

## 7. Resultados negativos

Resultados nulos, negativos, contraditórios ou favoráveis ao baseline devem ser preservados. Nenhum caso poderá ser apagado por contrariar a hipótese.

## 8. Separação de funções

CODEX poderá implementar instrumentos e logs, mas não decidir retroativamente critérios de sucesso. O pesquisador não poderá converter implementação correta em evidência favorável sem execução e análise.

## 9. Ensino

Material para Charlie Echo da Costa será produzido depois de haver conhecimento suficientemente validado e legitimamente transferível. O ensino não integra a variável primária desta pesquisa.

**Princípio:** pré-registrar para que a conclusão seja consequência dos dados, e não condição para escolher os dados.
