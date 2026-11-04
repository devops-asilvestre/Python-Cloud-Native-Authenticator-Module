from collections.abc import AsyncIterator

from identity_service.application.handlers.user_handlers import UserHandlers
from identity_service.infrastructure.cache.in_memory_cache import InMemoryUserCache
from identity_service.infrastructure.events.event_publisher import InMemoryUserEventPublisher
from identity_service.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyUserRepository,
)
from shared.persistence.database_settings import DatabaseSettings
from shared.persistence.session_factory import SessionFactory
from shared.persistence.unit_of_work import SqlAlchemyUnitOfWork

_cache = InMemoryUserCache()
_publisher = InMemoryUserEventPublisher()
_idempotency: dict[str, tuple[object, str]] = {}
_session_factory = SessionFactory(settings=DatabaseSettings())


async def get_handlers() -> AsyncIterator[UserHandlers]:
    async with SqlAlchemyUnitOfWork(_session_factory) as unit_of_work:
        yield UserHandlers(
            SqlAlchemyUserRepository(unit_of_work.session),
            _cache,
            _publisher,
            idempotency=_idempotency,
        )
