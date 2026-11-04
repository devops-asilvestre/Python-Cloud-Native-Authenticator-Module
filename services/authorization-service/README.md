# Authorization Service

**Bounded context:** Authorization & Policy (core).

Responsabilidade proposta: papéis, políticas RBAC/ABAC e decisões de acesso
tenant-aware, com negação por padrão. O contexto de autorização não autentica
usuários; uma autenticação bem-sucedida não concede autorização implicitamente.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Deve consumir contratos explícitos e
não importar módulos internos de outros contextos.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
