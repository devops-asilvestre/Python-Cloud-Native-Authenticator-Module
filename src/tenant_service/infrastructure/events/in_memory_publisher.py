from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.events import TenantDomainEvent


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.events: list[tuple[TenantDomainEvent, Tenant]] = []

    async def publish(self, event: TenantDomainEvent, tenant: Tenant) -> None:
        self.events.append((event, tenant))
