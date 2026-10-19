# Cloud Native Authenticator Platform

Fundação arquitetural de uma plataforma de identidade e acesso multi-tenant,
preparada para Python 3.13+, FastAPI, DDD, Clean Architecture, AWS e evolução
para microsserviços. Este repositório ainda contém um scaffold FastAPI mínimo
em `src/identity_service`; os diretórios em `services/` documentam limites de
bounded contexts futuros e não são implementações de serviços.

## Estrutura

| Diretório | Responsabilidade |
|---|---|
| [`services/`](services/README.md) | Limites arquiteturais dos bounded contexts e guias de serviço. |
| [`shared/`](shared/README.md) | Contratos e capacidades transversais com dependências controladas. |
| [`infrastructure/`](infrastructure/README.md) | Docker local, Terraform, ambientes e scripts operacionais. |
| [`docs/`](docs/README.md) | Arquitetura, ADRs, histórias, segurança e operações. |
| [`tests/`](tests/README.md) | Testes unitários, integração, contrato, arquitetura e E2E. |
| [`tools/`](tools/README.md) | Ferramentas de desenvolvimento e automação do repositório. |
| `src/identity_service` | Scaffold Python existente, preservado nesta história. |

O mapa de domínios e as responsabilidades propostas estão em
[`docs/architecture/domain-and-context-map.md`](docs/architecture/domain-and-context-map.md).
Os ADRs ficam em [`docs/adr/`](docs/adr/); histórias existentes continuam em
[`4dev/user_stories/`](4dev/user_stories/).

## Desenvolvimento local

Consulte o guia de [desenvolvimento local](LOCAL_DEVELOPMENT.md) para
pré-requisitos, configuração segura, portas, persistência e operação em
Windows/Linux. A pilha inclui PostgreSQL, Redis, DynamoDB Local, Jaeger,
Prometheus, Grafana, Mailpit e OpenTelemetry Collector; LocalStack não é
utilizado. O [troubleshooting](LOCAL_TROUBLESHOOTING.md) e os
[smoke tests](SMOKE_TESTS.md) documentam diagnóstico e validação.

O Compose exige `POSTGRES_PASSWORD` e `GRAFANA_ADMIN_PASSWORD` no ambiente do
processo. Após configurá-las localmente, inicie e valide os serviços:

```text
python infrastructure/scripts/local_platform.py start
python infrastructure/scripts/local_platform.py smoke-test
```

O guia detalhado do Compose está em
[`infrastructure/docker/README.md`](infrastructure/docker/README.md).

## Como testar

Na raiz do repositório, com as dependências de desenvolvimento instaladas:

```powershell
.\.venv\Scripts\pytest.exe -q
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe src tests
```

Os testes de arquitetura verificam os diretórios e READMEs dos bounded
contexts em `tests/architecture/`. Os testes existentes também exercitam o
scaffold atual; essas verificações não validam funcionalidades ainda não
implementadas.

Para executar os smoke tests de infraestrutura local, consulte
[SMOKE_TESTS.md](SMOKE_TESTS.md). Eles validam health checks, serviços e
endpoints do Compose sem criar dados de negócio.

### Scaffold FastAPI

O scaffold pode ser iniciado separadamente seguindo as instruções em
[`4dev/README.md`](4dev/README.md). Com a aplicação em execução, valide a rota
de liveness:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health/live
```

### Escopo das verificações

Os diretórios de serviços são placeholders arquiteturais: ainda não há seis
microsserviços executáveis. O Compose valida dependências locais, não fluxos de
autenticação, integração de eventos ou implantação AWS. O scaffold ainda não
envia telemetria ao OpenTelemetry Collector. A configuração desta fundação não
implementa regras de negócio, endpoints de domínio ou schemas de persistência.

As regras globais para contribuições futuras estão em
[`.github/copilot-instructions.md`](.github/copilot-instructions.md). Nenhuma
regra de negócio, endpoint ou schema de persistência é introduzido pela
fundação arquitetural.
