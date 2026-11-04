# Shared Cache Foundation

O módulo `shared.cache` expõe uma base para Redis assíncrono com isolamento de tenant,
serialização JSON e contratos análogos ao padrão de `shared.persistence`.

## Conteúdo

- `settings/redis_settings.py`: configuração via `pydantic-settings`
- `connection/connection_factory.py`: fábrica de clientes Redis async
- `connection/redis_provider.py`: provider que centraliza ciclo de vida do cliente
- `contracts/*`: interfaces para cache, locks e rate limiting
- `serialization/json_serializer.py`: serialização JSON para payloads de cache
- `keys/*`: construção de chaves com namespace e tenant
- `locks/redis_distributed_lock.py`: lock distribuído em Redis
- `rate_limit/redis_rate_limiter.py`: limitador de taxa em Redis
- `testing/*`: fixtures e dummies para testes unitários

## Regras arquiteturais

- A aplicação não acessa `redis.asyncio.Redis` diretamente.
- Todos os serviços usam o provider e contratos compartilhados.
- Chaves devem incluir `tenant_id` quando a operação for multi-tenant.
- A serialização segue JSON para compatibilidade com AWS ElastiCache e MemoryDB.
- O fluxo é: aplicação -> contrato -> provider -> Redis.

## Exemplo

```python
from shared.cache.provider.cache_provider import RedisCacheProvider
from shared.cache.connection.redis_provider import RedisClientProvider

provider = RedisClientProvider()
cache = RedisCacheProvider(client_provider=provider)

# no contexto de aplicação real: a API fica isolada de redis-py
# apenas via provider e contratos.
```
