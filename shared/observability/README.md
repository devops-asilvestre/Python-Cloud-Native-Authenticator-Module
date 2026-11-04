# Observabilidade compartilhada

[`src/shared/observability/`](../../src/shared/observability/__init__.py)
define `CorrelationContext` e os tipos `CorrelationId`, `RequestId` e `TraceId`,
além de contratos `StructuredLogger`, `Tracer`, `Span`, `Counter` e `Histogram`.
Os contratos são independentes de provedor e podem ser implementados por
adaptadores OpenTelemetry.

Telemetria não substitui registros de auditoria. Instrumentação deve preservar
correlação sem expor credenciais, tokens, atributos pessoais desnecessários ou
claims completos. A configuração inicial do OpenTelemetry Collector para o
ambiente local está em
[`infrastructure/docker/observability/`](../../infrastructure/docker/observability/);
esta pasta não inicia spans, exporta métricas nem configura instrumentação.
