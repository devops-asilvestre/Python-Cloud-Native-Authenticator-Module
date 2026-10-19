# Observabilidade compartilhada

Reservado a convenções técnicas de OpenTelemetry para traces, métricas e logs.
Telemetria não substitui registros de auditoria.

Instrumentação deve preservar correlação sem expor credenciais, tokens,
atributos pessoais desnecessários ou claims completos. A configuração inicial
do OpenTelemetry Collector para o ambiente local está em
[`infrastructure/docker/observability/`](../../infrastructure/docker/observability/);
esta pasta não contém implementação de instrumentação nesta história.
