"""Observability wrapper for EventBridge publication details."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EventObservability:
    """Structured metadata recorded around EventBridge publication."""

    publish_latency_ms: int = 0
    routing_latency_ms: int = 0
    publish_success: bool = True
    publish_failure: bool = False
    retry_count: int = 0

    def to_dict(self) -> dict[str, int | bool]:
        return {
            "publish_latency_ms": self.publish_latency_ms,
            "routing_latency_ms": self.routing_latency_ms,
            "publish_success": self.publish_success,
            "publish_failure": self.publish_failure,
            "retry_count": self.retry_count,
        }
