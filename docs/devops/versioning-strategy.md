# Estratégia de versionamento

## SemVer

O pacote usa `MAJOR.MINOR.PATCH` conforme Semantic Versioning:

- **MAJOR:** mudança incompatível na API ou contrato público.
- **MINOR:** funcionalidade compatível com versões anteriores.
- **PATCH:** correção compatível sem ampliação incompatível do contrato.

Enquanto a versão for `0.y.z`, a API ainda pode evoluir; ainda assim, cada
release deve documentar alterações e evitar incompatibilidades desnecessárias.
A versão atual é mantida em `[project].version` no `pyproject.toml`.

## Tags e pré-lançamentos

- Tags de release estável: `vMAJOR.MINOR.PATCH`, por exemplo `v1.2.3`.
- Não reutilizar nem mover tags publicadas.
- Pré-lançamentos, se adotados, devem usar identificador SemVer, como
  `1.2.3-rc.1`, e não são publicados pelo workflow estável atual, que aceita
  apenas tags `vX.Y.Z`.
- A tag estável deve apontar para commit integrado em `main`, com o mesmo
  número de versão registrado no `pyproject.toml`.

## Dependências

Restrições de dependências em `pyproject.toml` definem intervalos suportados;
atualizações devem ser revisadas, testadas e registradas. Ver
[gerenciamento de dependências](dependency-management.md).
