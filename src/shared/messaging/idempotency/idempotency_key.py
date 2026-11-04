"""Stable idempotency key."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdempotencyKey:
    """Tenant-scoped event identity used for durable processing claims."""

    tenant_id: str
    event_id: str

    def __post_init__(self) -> None:
        if not self.tenant_id.strip() or not self.event_id.strip():
            raise ValueError("Idempotency key values cannot be empty.")

    @property
    def value(self) -> str:
        return f"{self.tenant_id}:{self.event_id}"
