# Ambiente local de desenvolvimento

Este guia prepara a plataforma local de dependências para Windows ou Linux.
O Compose executa apenas componentes de suporte; não inicia APIs nem
microsserviços da plataforma.

## Pré-requisitos

- Docker Desktop no Windows ou Docker Engine no Linux, com Docker Compose v2.
- Python 3.13 ou superior.
- Acesso às imagens Docker na primeira inicialização.

## Configuração

O Compose exige duas senhas definidas somente no ambiente do processo:

| Variável | Uso |
|---|---|
| `POSTGRES_PASSWORD` | Senha do usuário local `authenticator` do PostgreSQL. |
| `GRAFANA_ADMIN_PASSWORD` | Senha local do usuário administrador `admin` do Grafana. |

Não use senhas de produção, não as grave em arquivos versionados e não
compartilhe os valores. Redis, DynamoDB Local e Mailpit não autenticam clientes
nesta configuração; mantenha seus endpoints acessíveis somente localmente.

### PowerShell

Digite as senhas nos prompts ocultos. Os valores ficam no ambiente do processo
atual até serem removidos ou a janela ser fechada:

```powershell
$secret = Read-Host "Senha local do PostgreSQL" -AsSecureString
$env:POSTGRES_PASSWORD = [System.Net.NetworkCredential]::new("", $secret).Password
$secret = Read-Host "Senha local do Grafana" -AsSecureString
$env:GRAFANA_ADMIN_PASSWORD = [System.Net.NetworkCredential]::new("", $secret).Password
```

### Bash (Linux)

```bash
read -rsp "Senha local do PostgreSQL: " POSTGRES_PASSWORD; echo
export POSTGRES_PASSWORD
read -rsp "Senha local do Grafana: " GRAFANA_ADMIN_PASSWORD; echo
export GRAFANA_ADMIN_PASSWORD
```

## Inicialização e operação

Execute os comandos na raiz do repositório. O script Python usa o Compose
versionado, aguarda os health checks ao iniciar e funciona nos dois sistemas:

```text
python infrastructure/scripts/local_platform.py start
python infrastructure/scripts/local_platform.py health-check
python infrastructure/scripts/local_platform.py smoke-test
```

Para validar a configuração sem iniciar os serviços:

```text
docker compose -f infrastructure/docker/compose.yaml config --quiet
```

Para ver o estado e os logs:

```text
docker compose -f infrastructure/docker/compose.yaml ps
docker compose -f infrastructure/docker/compose.yaml logs --follow
```

Para reiniciar os containers preservando os dados e aguardar que voltem a ficar
saudáveis:

```text
python infrastructure/scripts/local_platform.py restart
```

Para encerrar, mantendo os volumes:

```text
python infrastructure/scripts/local_platform.py stop
```

`docker compose down -v` remove permanentemente os dados locais persistidos.
Use-o somente se quiser descartar PostgreSQL, Redis, DynamoDB Local, Jaeger,
Prometheus, Grafana e Mailpit.

## Serviços, portas e acesso

As portas publicadas são vinculadas a `127.0.0.1`; não são expostas à rede
local. Os containers compartilham a rede bridge dedicada `local-platform`,
isolada das redes de outros projetos Compose. Como os serviços precisam estar
acessíveis pelo host, essa rede permite saída de rede pelo Docker.

| Serviço | Porta local | Protocolo / finalidade |
|---|---:|---|
| PostgreSQL | `5432` | TCP, banco `authenticator`, usuário `authenticator`. |
| Redis | `6379` | TCP, sem autenticação nesta configuração local. |
| DynamoDB Local | `18000` | HTTP, endpoint `http://127.0.0.1:18000`. |
| Jaeger | `16686` | Interface web em `http://127.0.0.1:16686`. |
| Prometheus | `9090` | Interface e API em `http://127.0.0.1:9090`. |
| Grafana | `3000` | Interface web em `http://127.0.0.1:3000`. |
| Mailpit | `1025` | SMTP local, sem TLS/autenticação. |
| Mailpit | `8025` | Interface e API em `http://127.0.0.1:8025`. |
| OpenTelemetry Collector | `4317` | OTLP sobre gRPC. |
| OpenTelemetry Collector | `4318` | OTLP sobre HTTP. |
| OpenTelemetry Collector | `13133` | Endpoint local de health check. |

O Collector recebe traces, métricas e logs OTLP. Os traces seguem para Jaeger,
as métricas são expostas para coleta pelo Prometheus e os logs são encaminhados
ao log do container do Collector. A instrumentação das aplicações não faz parte
desta configuração.

## Persistência e segurança

Volumes nomeados mantêm os dados entre `stop`, `down` e reinicializações. As
senhas são obrigatórias e externalizadas; nenhum valor de senha padrão é
fornecido. Redis, DynamoDB Local e Mailpit não autenticam clientes neste
ambiente, portanto não publique suas portas além do loopback. Esta plataforma
é apenas para desenvolvimento e não fornece configuração de produção.

Remova as senhas do processo ao terminar:

```powershell
Remove-Item Env:POSTGRES_PASSWORD
Remove-Item Env:GRAFANA_ADMIN_PASSWORD
```

```bash
unset POSTGRES_PASSWORD GRAFANA_ADMIN_PASSWORD
```

Consulte [LOCAL_TROUBLESHOOTING.md](LOCAL_TROUBLESHOOTING.md) para diagnóstico
e [SMOKE_TESTS.md](SMOKE_TESTS.md) para os testes de validação.
