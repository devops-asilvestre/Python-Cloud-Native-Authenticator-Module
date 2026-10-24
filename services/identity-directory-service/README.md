# Identity Directory Service

**Bounded context:** Identity Directory (supporting).

Responsabilidade proposta: ciclo de vida de identidades, grupos e atributos de
perfil dentro do tenant. Não autentica usuários, não armazena segredos de
autenticação e não define permissões.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Integrações futuras devem usar contratos
explícitos e não importar módulos internos de outros contextos.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
