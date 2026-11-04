# US025A - Validação do LocalStack

## Escopo

Esta evidência valida que o backend AWS local sobe no Docker Desktop sem
depender de uma conta AWS real. O serviço LocalStack habilita `events`, `sqs` e
`secretsmanager`; o script de inicialização cria os recursos necessários de
forma idempotente.

## Execução

Na raiz do repositório, com Docker Desktop em execução:

```powershell
$env:POSTGRES_PASSWORD = "local-only"
$env:GRAFANA_ADMIN_PASSWORD = "local-only"
docker compose -f infrastructure/docker/compose.yaml up -d --wait
curl.exe http://127.0.0.1:4566/_localstack/health
```

Resultado esperado: a resposta de saúde contém `events`, `sqs` e
`secretsmanager` como `available` e o container `localstack` aparece como
`healthy`.

## Evidência registrada

- Endpoint local: `http://127.0.0.1:4566`
- Região: `us-east-1`
- Credenciais: somente credenciais locais (`local`), sem segredo persistido
- Recursos provisionados automaticamente pelo
  [`01-provision-authentication-events.sh`](../../../infrastructure/docker/localstack/init/01-provision-authentication-events.sh)

## Status

Executar os comandos acima durante a certificação e anexar a saída do
healthcheck ao relatório da execução.
