"""Test and example event factories."""

from shared.events.testing.fake_events import (
    FAKE_EVENT_TYPE,
    FAKE_EVENT_VERSION,
    FakeUserCreatedPayload,
    make_fake_event_registry,
    make_fake_user_created_event,
)
from shared.events.testing.fixtures import make_event

__all__ = [
    "FAKE_EVENT_TYPE",
    "FAKE_EVENT_VERSION",
    "FakeUserCreatedPayload",
    "make_event",
    "make_fake_event_registry",
    "make_fake_user_created_event",
]
