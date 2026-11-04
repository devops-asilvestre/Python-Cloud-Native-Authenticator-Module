"""Shared Redis cache foundation for multi-tenant platform services."""

from shared.cache.connection.connection_factory import ConnectionFactory, RedisConnectionFactory
from shared.cache.connection.redis_provider import RedisClientProvider
from shared.cache.contracts.async_cache_contract import AsyncCacheContract
from shared.cache.contracts.cache_contract import CacheContract
from shared.cache.contracts.lock_contract import DistributedLockContract, LockContract
from shared.cache.contracts.rate_limit_contract import RateLimitContract
from shared.cache.contracts.session_cache_contract import SessionCacheContract
from shared.cache.contracts.token_cache_contract import TokenCacheContract
from shared.cache.exceptions.connection_exception import CacheConnectionException
from shared.cache.exceptions.redis_exception import RedisException
from shared.cache.keys.cache_key_builder import CacheKeyBuilder
from shared.cache.keys.tenant_key_builder import TenantAwareKeyBuilder
from shared.cache.locks.redis_distributed_lock import RedisDistributedLock
from shared.cache.provider.cache_provider import CacheProvider, RedisCacheProvider
from shared.cache.rate_limit.redis_rate_limiter import RedisRateLimiter
from shared.cache.serialization.json_serializer import JsonSerializer
from shared.cache.settings.redis_settings import RedisSettings

__all__ = [
    "AsyncCacheContract",
    "CacheConnectionException",
    "CacheContract",
    "CacheKeyBuilder",
    "CacheProvider",
    "ConnectionFactory",
    "DistributedLockContract",
    "JsonSerializer",
    "LockContract",
    "RateLimitContract",
    "RedisCacheProvider",
    "RedisClientProvider",
    "RedisConnectionFactory",
    "RedisDistributedLock",
    "RedisException",
    "RedisRateLimiter",
    "RedisSettings",
    "SessionCacheContract",
    "TenantAwareKeyBuilder",
    "TokenCacheContract",
]
