# Tenant Service

**Bounded context:** Tenant & Organization (supporting).

Responsabilidade proposta: ciclo de vida, configuração e estado de tenants e
organizações. O contexto é autoridade sobre seus identificadores e estado; não
é proprietário das identidades de usuário.

O contexto executável está em [`src/tenant_service`](../../src/tenant_service).
Ele contém o agregado `Tenant`, objetos de valor, handlers, contratos de
repositório/cache/eventos e a API REST. PostgreSQL, Redis e EventBridge são
adaptadores substituíveis das foundations compartilhadas; a camada de domínio
não conhece essas tecnologias.

Endpoints: `POST /tenants`, `GET/PUT /tenants/{id}`, ações de ciclo de vida e
`DELETE /tenants/{id}`. Outros contextos devem consumir eventos versionados e
contratos explícitos, validar o tenant no servidor e não importar
implementações internas deste contexto.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
