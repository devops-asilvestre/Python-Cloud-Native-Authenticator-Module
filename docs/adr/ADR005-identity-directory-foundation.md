# ADR005 — Identity Directory como bounded context

## Status

Aceita

## Decisão

O diretório é um bounded context próprio, com `User` como aggregate root,
value objects imutáveis, comandos/queries separados e ports para persistência,
cache e publicação de eventos. O escopo do tenant vem de contexto de requisição
(`X-Tenant-Id`) e é validado no servidor.

## Consequências

O contexto permanece independente de autenticação e autorização. A publicação
de eventos usa contratos versionados e adaptadores das foundations compartilhadas;
uma futura implementação transacional deve usar outbox para evitar perda entre
persistência e entrega.
