"""Small assertion helpers for contract and domain-event tests."""

from collections.abc import Sequence

from shared.kernel.domain_events import DomainEvent


def assert_event_types(
    events: Sequence[DomainEvent],
    expected_types: Sequence[type[DomainEvent]],
) -> None:
    """Assert that events have the expected concrete types in order."""
    actual_types = tuple(type(event) for event in events)
    if actual_types != tuple(expected_types):
        expected = tuple(expected_types)
        raise AssertionError(
            f"Expected event types {expected!r}, got {actual_types!r}."
        )
