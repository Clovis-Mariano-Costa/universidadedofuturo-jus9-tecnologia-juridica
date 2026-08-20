# Relatório de implementação — Pacote 12 V2

**Pedido selecionado:** [Drive — Pacote 12 ASM/GHR/GV](https://docs.google.com/document/d/17ZOWgB-YTWo-e9T_j6EC-UCPF9ExLq60iMuFrpjgxy4/edit?usp=drivesdk)  
**Duplicata histórica verificada:** [Drive — segunda cópia](https://docs.google.com/document/d/1W9KTPeV0ddki0VJ1PePl91ap_VzcWiae1yBN09WBJkA/edit?usp=drivesdk)  
**Estado original do pedido:** PENDENTE / especificação selecionada  
**Estado desta implementação:** CONCLUIDA_LOCALMENTE / SEM MERGE / SEM DEPLOY  
**Data:** 2026-08-11 America/Sao_Paulo

## Entrega

- `core.py`: ASM, GHR, hash SHA-256, eventos de proveniência, validação fail-closed
  e rollback append-only;
- `tests/test_package12.py`: unitários, integração, adversariais e regressão dos
  casos de aceite;
- `README.md` e `SECURITY.md`: uso, limites e controles;
- nenhum arquivo de rota pública, norma, Biblioteca ou frontend foi alterado.

## Evidências

O teste válido percorre `M21 -> M22` somente com recibo, versão/hash e controles
de segurança. Hash divergente, depósito sem hash, homologação sem evidência,
alteração sem nova versão, terminal forçado e vulnerabilidade alta sem aceitação
humana são bloqueados. Rollback gera nova versão e preserva três eventos no
histórico do teste.

## Limitações

Os dados são sintéticos. O pacote não se conecta ao Drive e não transforma o
modelo interno em decisão de banca, homologação, publicação ou autoridade
externa. Revisão humana continua necessária.
