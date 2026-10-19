# Authentication Service

**Bounded context:** Authentication & Assurance (core).

Responsabilidade proposta: verificação de autenticadores, desafios MFA,
recuperação, controles de tentativa e resultado/nível de garantia da
autenticação. Segredos e material de verificação nunca devem ser publicados em
eventos ou logs.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Deve consumir contratos publicados de
tenant e diretório, sem dependência de seus módulos internos.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
