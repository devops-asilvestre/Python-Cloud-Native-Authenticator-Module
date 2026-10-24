# Definition of Done

Uma história ou correção está concluída quando todos os itens aplicáveis forem
atendidos:

- Critérios de aceitação revisados e comportamento entregue, sem escopo
  pendente oculto.
- Implementação segue arquitetura, convenções e requisitos de privacidade.
- Testes relevantes adicionados/atualizados e executados; CI obrigatório
  aprovado (Ruff, mypy, pytest e verificações de segurança aplicáveis).
- Revisão por pares concluída; aprovação de CODEOWNER obtida quando aplicável.
- Riscos de autenticação, autorização, tenancy, dados pessoais, dependências e
  migrações foram avaliados.
- Documentação operacional e de usuário atualizada; ADR criado/atualizado para
  decisões arquiteturais duradouras.
- Logs e telemetria não expõem segredos ou dados pessoais desnecessários.
- PR vinculado à história/issue, evidências anexadas e conversas resolvidas.
- Mudança integrada à branch de destino; para release, versão, changelog/notas,
  tag e artefatos seguem a estratégia de release.

Se um item não for aplicável, explicitar a justificativa na descrição do PR.
