# Material de ensino — Automação governada da Universidade

**Estado:** `MATERIAL_DIDATICO_INTERNO / APRENDIZAGEM_PENDENTE_DE_VERIFICACAO`

## Ideia central

Automatizar não é conceder autoridade. O sandbox separa registro, validação, decisão experimental, revisão humana e efeito externo.

## Contraexemplos

- uma norma protegida não pode ser alterada porque um arquivo foi editado;
- uma fonte sem identificador não vira fonte confiável por possuir uma URL;
- uma IA não pode decidir externamente porque recebeu o papel de `judge_ai`;
- rollback preserva o histórico e não apaga o evento que falhou.

## Exercício

Dado um caso com `jurisdiction_label=STATE_COURT`, conflito não resolvido e `human_gate=false`, identifique três bloqueios e explique por que uma decisão interna não pode produzir efeito externo.

## Limite

Este material ensina o sandbox sintético. Não prova aprendizagem de Charlie Echo até que exista teste independente de compreensão.
