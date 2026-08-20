# Segurança do sandbox

- somente dados sintéticos;
- nenhuma credencial, sessão, token ou dado pessoal real;
- sem rede e sem integração externa no núcleo;
- falha fechada quando estado, transição, evidência, hash ou controle de
  segurança estiver incompleto;
- rollback adiciona versão e evento; não reescreve nem apaga histórico;
- publicação e efeitos transacionais continuam fora do escopo.
