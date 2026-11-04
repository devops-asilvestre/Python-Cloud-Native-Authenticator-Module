# Testes

Os testes seguem a separação por nível abaixo. Os pacotes e testes preexistentes
foram preservados; esta história adiciona verificações somente para a estrutura
arquitetural.

- [`unit/`](unit/): unidades isoladas, sem infraestrutura externa.
- [`integration/`](integration/): integração entre adaptadores e dependências.
- [`contract/`](contract/): compatibilidade de contratos entre contextos.
- [`e2e/`](e2e/): fluxos completos da plataforma.
- [`architecture/`](architecture/): limites e convenções estruturais.

Execute `pytest` na raiz. A automação de CI existente permanece fora do escopo
desta fundação.
