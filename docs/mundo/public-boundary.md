# Mundo - fronteira publica
STATE = SAFE_INFRASTRUCTURE_SCAFFOLD

MUNDO = fronteira entre o ecossistema interno e pessoas/sistemas externos.

## Invariantes
- publicacao externa exige estado honesto: pesquisa, demo, MVP, piloto, produto;
- nenhuma branch interna ou farda cria promessa comercial;
- dados reais, credenciais e segredos nao atravessam por padrao;
- entrada externa e untrusted ate validacao;
- spam e conteudo externo ficam em ingress/quarentena apropriados, nunca em canon por efeito proprio;
- produto para venda exige gates de seguranca, privacidade, operacao, suporte, rollback e responsabilidade comercial.

NEXT = ligar o primeiro produto vendavel somente apos o gate MVP10 definido no canone.
