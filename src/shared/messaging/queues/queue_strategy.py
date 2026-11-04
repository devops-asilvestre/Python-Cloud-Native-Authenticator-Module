"""Queue naming strategies."""

from typing import Protocol


class QueueStrategy(Protocol):
    """Map a bounded context and event type to a logical queue name."""

    def resolve(self, bounded_context: str, event_type: str) -> str: ...
