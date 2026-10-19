# Tenant Service

**Bounded context:** Tenant & Organization (supporting).

Responsabilidade proposta: ciclo de vida, configuração e estado de tenants e
organizações. O contexto é autoridade sobre seus identificadores e estado; não
é proprietário das identidades de usuário.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Outros contextos devem consumir um
contrato explícito de tenant e validar o tenant no servidor; não devem importar
implementações internas deste contexto.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
