# Arquitetura estratégica de domínio

Este diretório descreve a proposta de DDD estratégico para a plataforma. Os
contextos e integrações abaixo são decisões de desenho para orientar os
próximos requisitos e ADRs; não representam capacidades implementadas nem
certificação de conformidade.

## Documentos

- [Domínios, bounded contexts e context map](domain-and-context-map.md)
- [Mapa de serviços e limites de implantação](domain-and-context-map.md#mapa-de-servicos)
- [Catálogo de eventos](event-catalog.md)

## Premissas de leitura

- O produto é uma plataforma IAM SaaS multi-tenant, API-first, com OAuth2 e
  OpenID Connect como protocolos de integração.
- Isolamento de tenant, Zero Trust, menor privilégio, privacidade e segurança
  são requisitos transversais, não capacidades opcionais de um contexto.
- PostgreSQL, Redis, EventBridge, SQS, KMS, CloudWatch e X-Ray são escolhas de
  implementação planejadas; não definem, por si só, limites de domínio.
- Recomenda-se começar como monólito modular e evoluir limites de implantação
  com evidência operacional, sem antecipar microserviços.

## Estado

A aplicação atual é um scaffold FastAPI com liveness. Persistência, identidade,
autenticação, autorização, protocolos e publicação/consumo de eventos ainda
precisam ser implementados e validados.
