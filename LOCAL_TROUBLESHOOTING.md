# Troubleshooting do ambiente local

Execute os comandos na raiz do repositório. Não publique portas em interfaces
de rede nem copie senhas para logs ou relatórios.

## O Compose informa que uma variável obrigatória está ausente

Defina `POSTGRES_PASSWORD` e `GRAFANA_ADMIN_PASSWORD` no processo atual
conforme [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md), e tente novamente:

```text
docker compose -f infrastructure/docker/compose.yaml config --quiet
```

Não substitua as variáveis por senhas gravadas no `compose.yaml` ou em arquivos
versionados.

## Um container não inicia ou fica unhealthy

Consulte o estado e os logs do serviço:

```text
docker compose -f infrastructure/docker/compose.yaml ps
docker compose -f infrastructure/docker/compose.yaml logs --tail=100 <serviço>
```

Use um nome de serviço como `postgres`, `dynamodb-local` ou
`otel-collector`. Verifique espaço em disco, memória disponível e conflitos
nas portas listadas em [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md). Após
corrigir a causa, reinicie com:

```text
python infrastructure/scripts/local_platform.py restart
```

## Porta já está em uso

Feche o processo que utiliza a porta ou ajuste a porta publicada localmente no
Compose e na documentação. Preserve o endereço `127.0.0.1` no bind; não use
`0.0.0.0`, pois Redis, DynamoDB Local e Mailpit não exigem autenticação.

## Grafana não conecta ao Prometheus

O datasource provisionado usa o nome de serviço Docker `prometheus`. Dentro da
rede do Compose, não substitua o endereço por `localhost`. Verifique:

```text
docker compose -f infrastructure/docker/compose.yaml ps prometheus grafana
docker compose -f infrastructure/docker/compose.yaml logs --tail=100 prometheus grafana
```

## DynamoDB Local não responde ou perdeu dados

Confirme que o container está saudável e acessível na porta local `18000`.
DynamoDB Local usa o volume `dynamodb-data`; não execute `down -v` se precisar
preservar os dados. O smoke test usa credenciais fictícias aceitas somente pelo
endpoint local, nunca credenciais AWS.

## OpenTelemetry Collector não inicia

Verifique a configuração e os logs:

```text
docker compose -f infrastructure/docker/compose.yaml config --quiet
docker compose -f infrastructure/docker/compose.yaml logs --tail=100 otel-collector
```

O Collector requer Jaeger disponível para exportar traces. O endpoint de saúde
local é `http://127.0.0.1:13133/`. Este ambiente recebe traces, métricas e logs,
mas não instrumenta aplicações.

## Reinício, reconstrução e descarte de dados

`python infrastructure/scripts/local_platform.py restart` reinicia os
containers sem excluir os volumes e aguarda os health checks. O comando
`python infrastructure/scripts/local_platform.py stop` executa `docker compose down`,
também preservando os volumes. Somente use
`docker compose -f infrastructure/docker/compose.yaml down -v` quando aceitar
apagar todos os dados locais.

## Diagnóstico adicional

Consulte o resultado completo do teste automatizado:

```text
python infrastructure/scripts/local_platform.py smoke-test
```

O script reporta falhas por serviço e retorna código diferente de zero se
algum container ou endpoint não estiver saudável.
