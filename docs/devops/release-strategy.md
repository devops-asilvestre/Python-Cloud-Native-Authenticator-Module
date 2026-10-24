# Estratégia de release

## Modelo

Releases são preparadas a partir de `developer` em `release/x.y.z` e promovidas
por PR para `main`. Releases urgentes partem de `main` via `hotfix/*`. A versão
do pacote é definida em `pyproject.toml` e segue [SemVer](versioning-strategy.md).

## Publicação

1. Confirmar que o escopo está integrado em `developer`, os gates passaram e
   as mudanças visíveis ao consumidor estão documentadas.
2. Atualizar a versão em `pyproject.toml` e revisar notas de release.
3. Promover a release a `main` por PR aprovado.
4. Criar a tag anotada `vX.Y.Z` no commit integrado em `main`.
5. O workflow `Release` valida a tag, a versão do projeto e a ancestralidade
   do commit em `main`; então constrói wheel e sdist e cria uma GitHub Release
   com notas geradas.
6. Sincronizar `main` de volta a `developer` após a publicação.

O workflow não publica o pacote em um registry nem implanta serviço. Isso
exigirá configurar destino, proveniência/assinatura de artefatos, credenciais
federadas e aprovação apropriada antes de ampliar a automação.

## Correções e rollback

Publicar correção como nova versão patch, sem alterar uma release já publicada.
Para rollback, reverter a implantação no ambiente consumidor conforme o
procedimento daquele ambiente e publicar uma nova versão corretiva quando
necessário; não mover nem reutilizar tags.
