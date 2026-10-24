# Estratégia DevOps

## Objetivo e princípios

Esta estratégia define como mudanças são planejadas, construídas, verificadas
e disponibilizadas no Python Cloud Native Authenticator Module. O fluxo busca
entregas pequenas e rastreáveis, feedback automatizado, segurança desde o
início e responsabilidade compartilhada entre desenvolvimento e operação.

- Automatizar verificações repetíveis e manter resultados visíveis no GitHub.
- Proteger `main` e `developer` com revisão e verificações obrigatórias.
- Manter o menor privilégio em workflows, ambientes e credenciais.
- Versionar decisões e mudanças; não versionar segredos ou dados operacionais.
- Medir resultados para orientar melhoria contínua, sem usar métricas para
  comparar ou punir indivíduos.

## Fluxo de entrega

1. Registrar a história, critérios de aceitação, riscos e estratégia de teste
   na issue.
2. Criar uma branch curta a partir de `developer`, implementar e executar as
   verificações localmente.
3. Abrir pull request para `developer`; CI, revisão, gates de segurança e
   aprovação devem estar concluídos antes do merge.
4. Promover mudanças integradas de `developer` para `main` por pull request.
5. Atualizar a versão SemVer, mesclar a preparação de release em `main` e
   publicar a tag correspondente. O workflow constrói distribuições Python e
   cria uma GitHub Release; não realiza deploy de aplicação.
6. Acompanhar resultados, corrigir regressões e registrar decisões relevantes
   como ADRs.

## Automação e responsabilidades

- **CI:** Ruff, mypy e pytest em mudanças direcionadas às branches protegidas.
- **Segurança:** CodeQL, Bandit, pip-audit e revisão de dependências em pull
  requests; verificações recorrentes também ocorrem semanalmente.
- **Release:** valida correspondência entre tag e versão do `pyproject.toml`,
  exige que o commit da tag esteja integrado em `main`, constrói wheel e sdist
  e publica notas no GitHub.
- **Desenvolvimento:** autoria da mudança, testes, atualização da documentação
  e resposta aos comentários de revisão.
- **Revisores:** avaliar correção, segurança, arquitetura, testes e impacto
  operacional. CODEOWNERS orienta solicitações de revisão; regras de proteção
  devem ser configuradas nas definições do repositório.

## Escopo e evolução

Os workflows não fazem deploy, migração de banco, publicação em PyPI ou
aprovação de ambiente, pois esses destinos e requisitos ainda não estão
configurados. Qualquer introdução deve ser precedida por decisão explícita
sobre ambiente, credenciais federadas, aprovação, rollback e observabilidade.
Revisar esta estratégia quando mudar o modelo de branches, os destinos de
entrega ou os requisitos de segurança.

## Documentos relacionados

- [Git flow](git-flow.md), [estratégia de branches](branch-strategy.md) e
  [política de pull request](pull-request-policy.md).
- [Gates de qualidade](quality-gates.md), [gates de segurança](security-gates.md)
  e [Definition of Done](definition-of-done.md).
- [Estratégia de release](release-strategy.md), [versionamento](versioning-strategy.md)
  e [GitHub Actions](github-actions-strategy.md).
