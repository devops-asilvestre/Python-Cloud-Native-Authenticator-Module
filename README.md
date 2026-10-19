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

Requisitos: Docker com Docker Compose e Python 3.13+. A pilha local inclui
PostgreSQL, Redis, DynamoDB Local, Jaeger, Prometheus, Grafana, Mailpit e
OpenTelemetry Collector; LocalStack não é utilizado.

O Compose requer `POSTGRES_PASSWORD` e `GRAFANA_ADMIN_PASSWORD` no ambiente do
processo. Forneça valores localmente, fora do repositório, antes de iniciar:

```powershell
$env:POSTGRES_PASSWORD = Read-Host "Senha local do PostgreSQL"
$env:GRAFANA_ADMIN_PASSWORD = Read-Host "Senha local do Grafana"
docker compose -f infrastructure/docker/compose.yaml up -d
```

Os serviços publicados pelo Compose escutam somente em `127.0.0.1`. Consulte
[`infrastructure/docker/README.md`](infrastructure/docker/README.md) para
portas, configuração, encerramento e escopo da infraestrutura local.

O scaffold FastAPI atual pode ser executado separadamente, conforme as
instruções em [`4dev/README.md`](4dev/README.md).

## Como testar

### Testes automatizados

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

### Dependências locais com Docker Compose

Requer Docker Desktop ou Docker Engine com Compose. Defina senhas locais no
ambiente do processo — não as salve em arquivos versionados — e valide a
configuração antes de iniciar:

```powershell
$env:POSTGRES_PASSWORD = Read-Host "Senha local do PostgreSQL"
$env:GRAFANA_ADMIN_PASSWORD = Read-Host "Senha local do Grafana"

docker compose -f infrastructure/docker/compose.yaml config --quiet
docker compose -f infrastructure/docker/compose.yaml up -d
docker compose -f infrastructure/docker/compose.yaml ps
```

Confira a disponibilidade do PostgreSQL e Redis:

```powershell
docker compose -f infrastructure/docker/compose.yaml exec -T postgres pg_isready -U authenticator -d authenticator
docker compose -f infrastructure/docker/compose.yaml exec -T redis redis-cli ping
```

Confira os endpoints HTTP de Prometheus, Grafana e Mailpit:

```powershell
Invoke-RestMethod http://127.0.0.1:9090/-/healthy
Invoke-RestMethod http://127.0.0.1:3000/api/health
Invoke-RestMethod http://127.0.0.1:8025/api/v1/messages
```

Verifique o DynamoDB Local usando o `boto3` do projeto. O endpoint exige
requisições assinadas; as credenciais abaixo são valores fictícios aceitos
somente para este endpoint local e não são credenciais AWS:

```powershell
@'
import boto3

client = boto3.client(
    "dynamodb",
    endpoint_url="http://127.0.0.1:18000",
    region_name="us-east-1",
    aws_access_key_id="local",
    aws_secret_access_key="local",
)
print(client.list_tables())
'@ | python -
```

Jaeger UI: `http://127.0.0.1:16686`. Os demais endereços, portas e detalhes de
configuração estão em [`infrastructure/docker/README.md`](infrastructure/docker/README.md).
Todos os serviços publicados pelo Compose escutam somente em `127.0.0.1`.

Para parar os containers e manter seus dados locais:

```powershell
docker compose -f infrastructure/docker/compose.yaml down
```

Use `down -v` somente quando quiser remover também os volumes persistentes de
desenvolvimento.

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
