# Gates de qualidade

## Gates atuais de CI

O workflow `CI` executa em pushes e pull requests direcionados a `developer` e
`main`, com Python 3.13:

1. Instala o projeto e dependências opcionais `dev` declaradas em
   `pyproject.toml`.
2. Executa `ruff check .`.
3. Executa `mypy src tests`.
4. Executa `pytest` e gera relatório de cobertura em terminal e XML.

Todos os passos devem passar antes do merge. Corrigir o problema na origem;
não ignorar testes ou lint sem justificativa e revisão explícitas.

## Critérios de qualidade

- Testes unitários para regras de domínio e aplicação; testes de integração
  quando houver adaptadores externos, persistência ou contratos relevantes.
- Cobrir comportamento novo, caminhos de erro, autorização e isolamento por
  tenant. Não há atualmente um percentual global de cobertura configurado;
  evitar criar uma meta incompatível com a linha de base do scaffold. Estabelecer
  baseline medido e adotar meta progressiva antes de torná-la bloqueadora.
- Corrigir erros de tipo, lint e testes; não reduzir a qualidade existente sem
  aprovação e justificativa documentadas.
- Revisar dependências, migrações, documentação e efeitos operacionais junto
  com a mudança de código.

Configure o status do workflow CI como verificação obrigatória nas regras de
proteção do GitHub.
