from collections.abc import AsyncIterator

from identity_service.application.handlers.user_handlers import UserHandlers
from identity_service.infrastructure.cache.in_memory_cache import InMemoryUserCache
from identity_service.infrastructure.events.event_publisher import InMemoryUserEventPublisher
from identity_service.infrastructure.persistence.in_memory_repository import InMemoryUserRepository

_repository = InMemoryUserRepository()
_cache = InMemoryUserCache()
_publisher = InMemoryUserEventPublisher()
_idempotency: dict[str, tuple[object, str]] = {}


async def get_handlers() -> AsyncIterator[UserHandlers]:
    yield UserHandlers(_repository, _cache, _publisher, idempotency=_idempotency)  # type: ignore[arg-type]
