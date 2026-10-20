from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import pytest

from shared.kernel import (
    AggregateRoot,
    DomainEvent,
    DomainException,
    Entity,
    Result,
    ResultAccessError,
    SystemClock,
    ValueObject,
)


@dataclass(frozen=True, slots=True)
class Name(ValueObject):
    text: str

    @property
    def value(self) -> str:
        return self.text


class Item(Entity[int]):
    pass


@dataclass(frozen=True, slots=True)
class ItemCreated(DomainEvent):
    item_name: str = "item"


class ItemAggregate(AggregateRoot[int]):
    pass


def test_value_objects_compare_and_hash_by_value_and_type() -> None:
    assert Name("a") == Name("a")
    assert Name("a") != Name("b")
    assert len({Name("a"), Name("a")}) == 1


def test_entities_compare_by_concrete_type_and_identity() -> None:
    assert Item(1) == Item(1)
    assert Item(1) != Item(2)
    assert Item(1) != object()


def test_aggregate_root_collects_and_pulls_events() -> None:
    aggregate = ItemAggregate(1)
    event = ItemCreated()

    aggregate.add_domain_event(event)
    assert aggregate.domain_events == (event,)
    assert aggregate.pull_domain_events() == (event,)
    assert not aggregate.domain_events


def test_domain_event_has_utc_identity_and_type() -> None:
    event = ItemCreated()

    assert isinstance(event.event_id, UUID)
    assert event.occurred_at.tzinfo == UTC
    assert event.event_type == "ItemCreated"


def test_result_requires_access_to_the_matching_variant() -> None:
    success: Result[int, str] = Result.success(5)
    failure: Result[int, str] = Result.failure("bad")

    assert success.is_success and success.value == 5
    assert failure.is_failure and failure.error == "bad"
    with pytest.raises(ResultAccessError):
        _ = success.error
    with pytest.raises(ResultAccessError):
        _ = failure.value


def test_domain_exception_is_an_exception() -> None:
    with pytest.raises(DomainException):
        raise DomainException("domain failure")


def test_system_clock_returns_timezone_aware_utc_datetime() -> None:
    now = SystemClock().now()

    assert isinstance(now, datetime)
    assert now.tzinfo == UTC
