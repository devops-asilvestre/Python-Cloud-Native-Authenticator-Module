# ADR003: Fundação de EventBridge

- Status: Aceita
- Contexto: US022 - EventBridge Foundation
- Data: 2026-11-03

## Decisão

- Centralizar todo `PutEvents` no pacote `shared.eventbus`.
- Usar o contrato `EventEnvelope` de US018, com tenant, versão, correlação e
  trace obrigatórios.
- Resolver o barramento por tenant, categoria e tipo de evento antes da
  publicação.
- Usar filtragem, fanout, auditoria sanitizada, metadados de replay/archive e
  observabilidade como componentes explícitos da foundation.
- Manter proteção de detalhes opcional por um adaptador injetado do KMS de
  US020; o payload protegido nunca é enviado para logs.
- Delegar credenciais, região, endpoint local e criação do cliente ao AWS
  foundation existente.

## Consequências

Bounded contexts não precisam conhecer boto3 nem regras de EventBridge.
`EventBridgePublisher` valida o envelope, monta a entrada AWS, executa
`PutEvents` e expõe somente identificadores não sensíveis no resultado.
Falhas de publicação são explícitas e podem ser avaliadas por
`RetryPolicy`. Health checks usam `DescribeEventBus`.

Archive e replay possuem apenas metadata nesta história; a retenção e o replay
efetivos permanecem responsabilidades futuras.
