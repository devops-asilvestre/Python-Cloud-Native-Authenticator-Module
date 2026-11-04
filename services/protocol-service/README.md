# Protocol Service

**Bounded context:** Identity Protocols & Clients (supporting).

Responsabilidade proposta: contratos OAuth2/OIDC, registro de clientes e
tradução de scopes e claims. Deve delegar autenticação e autorização aos
respectivos contextos, sem duplicar suas políticas de domínio. Tokens e códigos
de autorização não devem ser publicados em eventos.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Integrações futuras devem usar contratos
explícitos, sem importações internas entre contextos.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
