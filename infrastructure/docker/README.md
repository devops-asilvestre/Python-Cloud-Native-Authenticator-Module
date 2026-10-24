# Ambiente local Docker

[`compose.yaml`](compose.yaml) inicia somente dependências locais:
PostgreSQL, Redis, DynamoDB Local, Jaeger, Prometheus, Grafana, Mailpit e
OpenTelemetry Collector. LocalStack não é utilizado. A aplicação não é
construída nem iniciada por este Compose.

## Operação

Defina `POSTGRES_PASSWORD` e `GRAFANA_ADMIN_PASSWORD` no ambiente do processo
conforme o guia de [desenvolvimento local](../../LOCAL_DEVELOPMENT.md). Não
grave os valores no repositório. Na raiz, execute:

```text
python infrastructure/scripts/local_platform.py start
python infrastructure/scripts/local_platform.py health-check
python infrastructure/scripts/local_platform.py smoke-test
```

Para encerrar mantendo os dados:

```text
python infrastructure/scripts/local_platform.py stop
```

O comando `docker compose down -v` remove todos os volumes persistentes; use-o
somente se quiser descartar os dados locais.

## Portas

| Serviço | Endereço local |
|---|---|
| PostgreSQL | `127.0.0.1:5432` |
| Redis | `127.0.0.1:6379` |
| DynamoDB Local | `http://127.0.0.1:18000` |
| Jaeger UI | `http://127.0.0.1:16686` |
| OpenTelemetry OTLP/gRPC | `127.0.0.1:4317` |
| OpenTelemetry OTLP/HTTP | `http://127.0.0.1:4318` |
| OpenTelemetry health check | `http://127.0.0.1:13133/` |
| Prometheus | `http://127.0.0.1:9090` |
| Grafana | `http://127.0.0.1:3000` |
| Mailpit SMTP | `127.0.0.1:1025` |
| Mailpit UI | `http://127.0.0.1:8025` |

Todas as portas publicadas são vinculadas ao loopback. Os serviços também
compartilham a rede bridge dedicada `local-platform`, isolada das redes de
outros projetos Compose. Redis, DynamoDB Local e Mailpit não autenticam
clientes nesta configuração. Os dados e credenciais destinam-se somente ao
desenvolvimento local.

Consulte [LOCAL_TROUBLESHOOTING.md](../../LOCAL_TROUBLESHOOTING.md) para
diagnóstico e [SMOKE_TESTS.md](../../SMOKE_TESTS.md) para detalhes das
verificações automatizadas.
