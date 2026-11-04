# US024 — Identity Directory Foundation

O bounded context Identity Directory gerencia identidades corporativas sem
implementar login, senha, autenticação, autorização, OAuth2 ou OIDC.

## Limites e segurança

- Toda operação exige um `TenantContext` confiável injetado por uma fronteira
  upstream (gateway/middleware). `X-Tenant-Id`, quando enviado, só confirma o
  contexto confiável; nunca é uma credencial nem escolhe o tenant sozinho.
- O email é normalizado para lowercase e é único por tenant.
- Exclusão é lógica (`DELETED`); registros não são removidos fisicamente.
- Eventos carregam somente IDs opacos, tenant e metadados de correlação.
- O contexto não importa módulos internos de `tenant_service`.

## API

`POST /users`, `GET /users/{id}`, `PUT /users/{id}`,
`POST /users/{id}/activate`, `/suspend`, `/deactivate`,
`DELETE /users/{id}` e `GET /users/search`.

O contrato OpenAPI é gerado pelo FastAPI em `/openapi.json` no ambiente local.
