# Guia de uso da observabilidade compartilhada

Use a estrutura do pacote para criar identificadores, contextos e registros sem
acoplar c?digo de neg?cio a SDKs de observabilidade espec?ficos.

## Exemplo de logging

```python
from shared.observability.context.request_context import RequestContext
from shared.observability.context.telemetry_context import TelemetryContext
from shared.observability.logging.structured_logger import StructuredLogger

request_context = RequestContext()
telemetry_context = TelemetryContext(
    service_name="authentication-service",
    component="identity",
    request_context=request_context,
)
logger = StructuredLogger("authentication-service", telemetry_context=telemetry_context)
logger.info("user-authenticated", user_id="user-123", password="secret")
```

Os valores sens?veis s?o automaticamente mascarados antes do registro.

## Exemplo de tracing

```python
from shared.observability.tracing.trace_context import TraceContext

trace_context = TraceContext()
headers = trace_context.to_headers()
```
