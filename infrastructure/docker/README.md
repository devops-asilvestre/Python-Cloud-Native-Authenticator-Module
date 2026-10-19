# Ambiente local Docker

[`compose.yaml`](compose.yaml) inicia dependências locais para desenvolvimento:
PostgreSQL, Redis, DynamoDB Local, Jaeger, Prometheus, Grafana, Mailpit e
OpenTelemetry Collector. LocalStack não é utilizado. A aplicação não é
construída nem iniciada por este Compose; o scaffold atual é executado à parte.

## Iniciar

Docker Compose e dois valores de ambiente locais são necessários. Defina
`POSTGRES_PASSWORD` e `GRAFANA_ADMIN_PASSWORD` no ambiente do processo, sem
registrá-los no repositório, e execute na raiz:

```powershell
docker compose -f infrastructure/docker/compose.yaml up -d
docker compose -f infrastructure/docker/compose.yaml ps
```

Para encerrar:

```powershell
docker compose -f infrastructure/docker/compose.yaml down
```

Use `down -v` somente se desejar remover explicitamente os volumes persistentes
de desenvolvimento.

## Endpoints locais

| Serviço | Endereço |
|---|---|
| PostgreSQL | `127.0.0.1:5432` |
| Redis | `127.0.0.1:6379` |
| DynamoDB Local | `http://127.0.0.1:18000` |
| Jaeger UI | `http://127.0.0.1:16686` |
| OpenTelemetry OTLP/gRPC | `127.0.0.1:4317` |
| OpenTelemetry OTLP/HTTP | `http://127.0.0.1:4318` |
| Prometheus | `http://127.0.0.1:9090` |
| Grafana | `http://127.0.0.1:3000` |
| Mailpit SMTP | `127.0.0.1:1025` |
| Mailpit UI | `http://127.0.0.1:8025` |

As portas são publicadas somente no loopback. Redis e DynamoDB Local não
fornecem autenticação nesta configuração, portanto mantenha-os locais e não
exponha as portas à rede. Os dados são de desenvolvimento, sem garantias de
durabilidade ou segurança de produção. A configuração de Collector/Prometheus
é mínima e não representa instrumentação da aplicação.
