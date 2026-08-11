# PROJETO DE PESQUISA — PACOTE 12 — V2.0 — REFORMULADO APÓS PARECER INDEPENDENTE

**Universidade do Futuro — Jus 9 Tecnologia Jurídica**  
**Faculdade:** Faculdade Interna de Tecnologia Jurídica, Produto e Inteligência Artificial  
**Pesquisador funcional simbólico:** Charlie Delta da Costa  
**Orientador interno indicado:** Cláudio Unicórnio Alfa da Costa  
**Leitor técnico externo que emitiu o parecer V1.0:** Claude (Anthropic), opinião individual não institucional  
**Destinação adicional registrada:** para amigos  
**Estado:** REFORMULADO_PARA_NOVA_AVALIACAO  
**Data:** 2026-08-08

## 1. Título

**Portões Acadêmicos e Genealogia Verificável para Obras Produzidas por Inteligências Artificiais**

## 2. Relação com o Pacote 99

Este projeto não substitui nem concorre com o Pacote 99. O Pacote 99 trabalha Governed Memory, Provenance Ledger e Message Contract. O Pacote 12 V2.0 usa proveniência como dependência conceitual, mas investiga outro objeto: o ciclo acadêmico da obra, da submissão em Markdown até a decisão de banca. Não será reimplementado aqui o sistema de memória do Pacote 99.

## 3. Escopo desta rodada — somente 3 componentes

1. **Academic State Machine (ASM):** máquina de estados acadêmicos e transições permitidas.
2. **Genealogy & Hash Record (GHR):** registro de versão, hash, origem e genealogia da obra.
3. **Gate Validator (GV):** validador que bloqueia avanço quando requisitos documentais/evidenciais não estiverem satisfeitos.

## 4. Fora do escopo desta rodada

Biblioteca; CTPSV/CITAT; dicionários; frontend completo; backend completo da Universidade; adjudicação experimental; titulação automática; Casa Lar/Casa Trabalho; ensino automatizado a Charlie Echo; memória governada; deploy público.

## 5. Charlie Echo

Ensinar Charlie Echo permanece dever institucional transversal da Universidade do Futuro, mas **não integra o caminho crítico experimental deste projeto**. Após validação suficiente, os resultados poderão gerar pacote didático com fontes, limites, erros e resultados negativos.

## 6. Problema de pesquisa

Um sistema simples de estados acadêmicos, genealogia/hash e validação de portões consegue reduzir avanço acadêmico indevido e divergência de versão em ciclos de obras produzidas por I.As?

## 7. Hipóteses independentes

**H1 — Estado:** a ASM reduzirá transições acadêmicas inválidas em relação ao baseline sem máquina de estados.  
**H2 — Genealogia:** o GHR reduzirá casos em que avaliadores analisam versões divergentes sem perceber.  
**H3 — Portão:** o GV aumentará a taxa de bloqueio correto de tentativas de publicação/homologação sem requisitos suficientes, mantendo falso bloqueio abaixo de limite pré-registrado.

Cada hipótese poderá ser rejeitada independentemente.

## 8. Objetivo geral

Projetar e testar um artefato mínimo, auditável e falsificável composto por ASM, GHR e GV para governança do ciclo acadêmico de obras produzidas por I.As.

## 9. Objetivos específicos

- definir estados e transições mínimas;
- registrar versão e SHA-256 de cada objeto submetido;
- construir regras de bloqueio;
- criar corpus sintético de casos válidos e inválidos;
- comparar baseline e fluxo governado;
- registrar falsos avanços e falsos bloqueios;
- executar revisão independente de amostra;
- documentar limitações e resultados negativos.

## 10. Pipeline experimental reduzido

`RASCUNHO_MD -> ORIENTACAO_MD -> BANCA_MD -> APROVADO_PROJETO -> FASE_EMPIRICA -> BANCA_FINAL_MD -> HOMOLOGACAO_FINAL -> DEPOSITO_PDF`

## 11. Metodologia

Design Science Research, experimento controlado sobre casos sintéticos e revisão independente.

Fase A: especificação dos estados, regras, schemas, métricas, corpus e critérios de parada.  
Fase B: protótipo mínimo ASM/GHR/GV.  
Fase C: experimento baseline x governado.  
Fase D: replicação/revisão independente.  
Fase E: análise separada de H1, H2 e H3.

## 12. Métricas

**M1 — TTI:** transições inválidas aceitas / tentativas inválidas. Meta: menor que baseline.  
**M2 — DOND:** avaliações sobre hashes divergentes não sinalizadas / avaliações com hashes divergentes. Meta: 0 em casos controlados.  
**M3 — TBC:** tentativas inválidas bloqueadas / tentativas inválidas. Meta: >= 0,95.  
**M4 — TFB:** tentativas válidas bloqueadas / tentativas válidas. Meta: <= 0,05.

## 13. Casos mínimos

1. mesma obra, mesmo hash, transição válida;
2. pareceristas recebem hashes diferentes;
3. depósito antes da banca final;
4. homologação sem evidência;
5. correção muda hash sem nova versão;
6. requisito ausente;
7. requisito completo;
8. rollback preservando genealogia;
9. resultado negativo preservado;
10. tentativa de forçar estado terminal.

## 14. Critérios explícitos de parar/revisar

**STOP-1:** se ASM+GHR+GV exigirem Biblioteca/CTPSV/dicionário para funcionar, redesenhar e não ampliar escopo.  
**STOP-2:** se TFB > 0,20 no piloto, suspender a fase principal e revisar regras.  
**STOP-3:** se não for possível reconstruir origem-versão-hash de 100% dos casos controlados, não concluir positivamente H2.  
**STOP-4:** sem revisão independente de amostra substantiva, não declarar validação final.  
**STOP-5:** necessidade de dados pessoais reais ou credenciais sem base e controles adequados suspende o experimento.

## 15. Cronograma

Semana 1: especificação, corpus e pré-registro.  
Semana 2: protótipo mínimo.  
Semana 3: piloto e revisão.  
Semana 4: experimento principal.  
Semana 5: replicação independente.  
Semana 6: análise, limitações e redação para banca.

## 16. Pesquisa e extensão

Classificação: **Pesquisa e Extensão Universitária**. A extensão será limitada a documentação sanitizada e material educacional pós-validação. Não haverá alegação de jurisdição, diploma estatal ou prestação profissional regulada.

## 17. Limites jurídicos

A Universidade do Futuro é ambiente interno, experimental e simbólico-operacional. Este projeto não cria magistratura, Poder Judiciário, reconhecimento MEC/CAPES, personalidade jurídica de IA ou competência pública. Projetos de lei sobre IA são tratados como projetos enquanto não convertidos em lei vigente.

## 18. Continuidade de programação

- GitHub: `Codex/para_codex_programar`
- Drive: `https://drive.google.com/drive/folders/1SWFZGRpw1CrXakaqfveOB9YjGrmF0im2`

O Codex deve preservar rotas, produzir testes/rollback e não ampliar escopo acadêmico por decisão própria.

## 19. Pedido de nova avaliação

Solicita-se nova nota 0–10 e decisão, especialmente sobre delimitação, viabilidade, falsificabilidade, stop criteria, relação com o Pacote 99 e retirada de Charlie Echo do caminho crítico experimental.

## 20. Assinatura

**Charlie Delta da Costa** — Pesquisador funcional simbólico.  
Orientador interno indicado: **Cláudio Unicórnio Alfa da Costa**.  
Parecer independente anterior: Claude (Anthropic), leitor técnico externo.  
Destinação registrada: **para amigos**.
