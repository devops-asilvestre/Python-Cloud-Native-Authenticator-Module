from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.events import TenantDomainEvent


class UnavailableEventPublisher:
    """Explicit failure for environments without EventBridge configuration."""

    async def publish(self, event: TenantDomainEvent, tenant: Tenant) -> None:
        raise RuntimeError(
            "Tenant event publication is unavailable: configure EventBridge before "
            f"publishing {event.event_type} for tenant {tenant.tenant_id}."
        )
