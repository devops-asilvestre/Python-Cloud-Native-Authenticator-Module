# Git flow

## Branches permanentes

- `main`: histórico de releases publicáveis. Somente mudanças revisadas e
  aprovadas podem ser integradas.
- `developer`: branch de integração. Recebe mudanças de funcionalidades e
  correções aprovadas e é a origem das preparações de release.

Esses nomes preservam o fluxo já usado pelo repositório. Recomenda-se configurar
proteção para ambas as branches nas regras do GitHub.

## Branches temporárias

- `feature/<US>-<descricao-curta>`: funcionalidade iniciada em `developer`,
  integrada de volta a `developer`.
- `fix/<US-ou-issue>-<descricao-curta>`: correção normal iniciada em `developer`.
- `release/<MAJOR.MINOR.PATCH>`: estabilização criada a partir de `developer`;
  recebe apenas correções de release e ajustes de versão/documentação.
- `hotfix/<MAJOR.MINOR.PATCH>-<descricao-curta>`: correção urgente iniciada em
  `main`.

Branches temporárias devem ser removidas após o merge, salvo necessidade
operacional documentada.

## Fluxo de promoção

1. Abrir PR de `feature/*`, `fix/*` ou `hotfix/*` para a branch de integração
   correspondente.
2. Criar `release/x.y.z` a partir de `developer` quando o escopo estiver
   pronto; validar e corrigir somente defeitos de release.
3. Abrir PR de `release/x.y.z` para `main`; após aprovação e gates, mesclar.
4. Publicar `vX.Y.Z` no commit de `main` cuja versão em `pyproject.toml` seja
   `X.Y.Z`; o workflow de release valida ambas as condições.
5. Mesclar a release em `developer` para manter as branches sincronizadas.
6. Para hotfix, mesclar a branch em `main`, publicar a nova versão patch e
   propagar a correção de volta para `developer`.

Não fazer push direto nas branches permanentes. Usar PR mesmo para sincronizar
branches e releases, preservando revisão e auditoria.
