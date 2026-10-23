# Contratos de eventos compartilhados

[`src/shared/events/`](../../src/shared/events/__init__.py) fornece contratos
agnósticos de transporte para eventos entre bounded contexts. A implementação
usa Pydantic v2, JSON UTF-8 e versões SemVer estáveis (`major.minor.patch`).
Nenhum adaptador EventBridge, SQS, SNS, DynamoDB Streams, fila ou barramento é
implementado nesta fundação.

## Envelope e metadados

`EventEnvelope` é imutável e contém `event_id`, `event_type`, `event_version`,
`correlation_id`, `trace_id`, `tenant_id`, `occurred_at`, `source_service` e o
payload específico do evento. IDs de correlação e trace são compatíveis com a
fundação de observabilidade. `EventContext.from_observability` copia esses IDs
de `RequestContext` e `TraceContext` sem compartilhar estado mutável.
`EventCorrelation` agrupa correlação, requisição e causação; `EventTraceContext`
carrega trace, span e amostragem. O envelope preserva `trace_id` como campo
obrigatório e também mantém os campos necessários para propagar o contexto de
span. `EventEnvelope.log` integra com `LoggerContract`/`StructuredLogger` e
registra somente IDs e tipo/versão, nunca o payload.

`tenant_id` e `source_service` são obrigatórios. Timestamps precisam ter fuso
horário e são normalizados para UTC. A validação de `tenant_id` neste pacote
não substitui autorização nem isolamento de tenant no serviço consumidor.

Nomes seguem `<bounded_context>.<aggregate>.<event>`, em letras minúsculas,
dígitos e hífens, por exemplo `identity.user.created`. A versão é metadado
separado (`1.0.0`), não um sufixo do nome. Mudanças compatíveis incrementam
minor ou patch; mudanças incompatíveis publicam uma nova versão major e devem
preservar os contratos já registrados.

## Registro, validação e JSON

Registre um modelo Pydantic específico por tipo e versão em `EventRegistry`.
Todos os schemas precisam fechar objetos (Pydantic `extra="forbid"`), inclusive
objetos aninhados; campos de mapa dinâmico não são aceitos como allowlist.
`EventSchemaValidator` rejeita tipos/versões sem registro e payloads que não
correspondam ao schema. `JsonEventSerializer` requer esse validador antes de
serializar. `EventDeserializer` rejeita JSON malformado, chaves duplicadas,
envelopes inválidos, schema ausente e payload incompatível.

O schema de cada payload deve ser uma allowlist mínima. O pacote não faz
mascaramento automático de payloads: não publique senhas, material de fatores,
tokens, códigos de autorização, chaves privadas, claims completos ou outros
segredos/dados excessivos. Dados pessoais exigem finalidade, base legal,
controle de acesso e retenção aprovados.

## Contratos assíncronos

`DomainEventContract` mantém eventos internos desacoplados de observabilidade e
infraestrutura. A conversão explícita para `EventEnvelope` ocorre antes da
publicação por `EventEnvelope.from_domain_event`: o produtor fornece nome e
versão estáveis, contexto confiável e payload allowlistado. O evento de domínio
nunca é serializado automaticamente. `IntegrationEventContract`, `EventPublisherContract`,
`EventSubscriberContract` e `EventHandlerContract` definem interfaces
assíncronas; adaptadores concretos pertencem às camadas de infraestrutura.

## Exemplo

```python
from pydantic import BaseModel, ConfigDict

from shared.events import (
    EventDeserializer,
    EventRegistry,
    EventSchemaValidator,
    EventVersion,
    JsonEventSerializer,
)
from shared.events.testing import make_fake_user_created_event


class UserCreatedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    user_id: str


registry = EventRegistry()
registry.register("identity.user.created", EventVersion(major=1), UserCreatedPayload)
validator = EventSchemaValidator(registry)
encoded = JsonEventSerializer(validator).serialize(make_fake_user_created_event())
decoded = EventDeserializer(validator).deserialize(encoded)
```

Um exemplo executável está em
[`examples/shared_events_usage.py`](../../examples/shared_events_usage.py).
O contrato anterior continua disponível pelos imports
`shared.events.contracts`, `shared.events.metadata`,
`shared.events.serializers` e `shared.events.versioning`.

Decisões e catálogo de tipos estão em
[`docs/adr/ADR002-event-contract-foundation.md`](../../docs/adr/ADR002-event-contract-foundation.md)
e [`docs/architecture/event-catalog.md`](../../docs/architecture/event-catalog.md).
