# Registro de execução — Mão na Massa — 2026-08-18

**Branch:** `codex/mao-na-massa-2026-08-18`  
**Casa de trabalho:** `SITE_SOURCE/CODEX/`  
**Estado:** `EM_REVISAO`  
**MGP-9:** preservado; POC confirmatória não executada.

## Entrega técnica

Foi criado `CODEX/runtime/` com funções locais e determinísticas para:

- canonicalização LF, serialização determinística e SHA-256;
- `execution_purpose` e `is_synthetic`, com bloqueio de sintéticos na porta B12;
- trava pré-geração para representação visual de PAI AMOR;
- registro de aprendizagem com tentativa, estado e revisão humana;
- infraestrutura BJI iniciando em `NAO_EXECUTADO` sem resultados ou conclusões;
- imutabilidade de normas protegidas;
- adjudicação explicitamente `INTERNAL_EXPERIMENTAL`, sem efeito estatal automático;
- transições acadêmicas com evidência obrigatória, manifesto de rollback e scanner de marcadores sensíveis.

## Evidência local

Comando:

```text
cd SITE_SOURCE/CODEX/runtime
npm test
```

Resultado inicial: **8 testes aprovados, 0 falhas**.  
Após a extensão de governança acadêmica: **11 testes aprovados, 0 falhas**.

O teste não gera imagem, não usa dado real, não executa a POC MGP-9 e não publica.

## Evidência pública da Tarefa 001

Em 2026-08-18, a verificação HTTP retornou:

| URL | Resultado |
|---|---:|
| `https://universidadedofuturo.jus9tecnologia.com.br/` | 200 |
| `https://universidadedofuturo.jus9tecnologia.com.br/para-humanos.html` | 200 |
| `https://universidadedofuturo.jus9tecnologia.com.br/sitemap.xml` | 200 |

Também foi verificado que a home aponta para `para-humanos.html`, o sitemap contém a rota, e a página tem viewport, navegação nomeada e elemento `main`. Não houve alteração de código para essa tarefa porque os critérios observáveis já estavam atendidos no commit público atual `ef1a522`.

## Limites e revisão necessária

- O runtime é uma biblioteca local; não afirma que o ecossistema inteiro já tem integração com banco, Drive, GitHub, RBAC/ABAC ou geradores externos.
- A verificação pública não substitui revisão manual completa em dispositivos móveis e teclado.
- A sincronização Drive ↔ GitHub foi inventariada, mas não houve cópia ou movimentação automática devido a duplicatas e divergências históricas.
- A implementação do runtime não altera corpus, método, hashes ou resultados MGP-9.

## Rollback

Reverter o commit desta branch ou remover o diretório `CODEX/runtime` e este registro. Nenhuma rota pública ou arquivo histórico precisa ser apagado para o rollback.
