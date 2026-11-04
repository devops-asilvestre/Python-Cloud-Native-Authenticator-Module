# Smoke tests da plataforma local

O teste automatizado verifica containers, health checks, conectividade aos
serviços e endpoints HTTP. Não cria APIs, tabelas de domínio ou dados de
negócio.

## Pré-requisitos

- Docker com Docker Compose v2.
- Python 3.13+ e dependências do projeto instaladas (`boto3` é usado para
  consultar o DynamoDB Local).
- Plataforma iniciada com as instruções de
  [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md).

## Executar

Na raiz do repositório:

```text
python infrastructure/scripts/local_platform.py smoke-test
```

O script primeiro exige que cada container esteja em estado `healthy`. Depois
valida PostgreSQL com `pg_isready`, Redis com `PING`, DynamoDB Local com
`list_tables` e os endpoints HTTP de Jaeger, OpenTelemetry Collector,
Prometheus, Grafana e Mailpit. Cada verificação imprime `PASS` ou `FAIL`; uma
falha retorna código de saída diferente de zero.

Para validar somente os health checks dos containers:

```text
python infrastructure/scripts/local_platform.py health-check
```

Para validar somente a sintaxe e interpolação do Compose sem iniciar serviços:

```text
docker compose -f infrastructure/docker/compose.yaml config --quiet
```

## Persistência

Os dados persistidos ficam em volumes nomeados. Para verificar a persistência
do Redis com um marcador temporário, execute:

```text
docker compose -f infrastructure/docker/compose.yaml exec -T redis redis-cli SET us011:persistence-check ok
python infrastructure/scripts/local_platform.py restart
docker compose -f infrastructure/docker/compose.yaml exec -T redis redis-cli GET us011:persistence-check
docker compose -f infrastructure/docker/compose.yaml exec -T redis redis-cli DEL us011:persistence-check
```

O valor esperado após o reinício é `ok`; o último comando remove o marcador.
Esse teste reinicia a plataforma e interrompe brevemente os serviços. O smoke
test normal não altera dados. `docker compose down -v` apaga todos os volumes
e deve ser reservado ao descarte intencional do ambiente.

## Limites

O smoke test confirma disponibilidade e conexão, não substitui testes de
integração, testes de persistência com dados de aplicação ou uma validação de
produção. Credenciais DynamoDB `local` usadas pelo teste são fictícias e
restritas ao endpoint DynamoDB Local.
