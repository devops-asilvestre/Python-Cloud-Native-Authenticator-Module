from identity_service.domain.entities import User
from identity_service.domain.events import UserDomainEvent


class InMemoryUserEventPublisher:
    def __init__(self) -> None:
        self.events: list[tuple[UserDomainEvent, User]] = []

    async def publish(self, event: UserDomainEvent, user: User) -> None:
        self.events.append((event, user))
