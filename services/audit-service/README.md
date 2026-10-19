# Audit Service

**Bounded context:** Audit & Privacy (supporting).

Responsabilidade proposta: evidências de ações administrativas e de segurança,
retenção, minimização e suporte a solicitações de titulares. Auditoria é
distinta de telemetria operacional e requer controle de acesso próprio.

Este diretório é somente um placeholder arquitetural. Não contém aplicação,
API, regras de negócio ou persistência. Eventos consumidos futuramente devem
ser minimizados e versionados; nunca devem incluir credenciais, tokens ou
segredos.

O desenho estratégico está em
[`docs/architecture/domain-and-context-map.md`](../../docs/architecture/domain-and-context-map.md).
