"""Domain-oriented building blocks without domain-specific behavior."""

from shared.kernel.aggregates import AggregateRoot
from shared.kernel.clocks import Clock, SystemClock
from shared.kernel.domain_events import DomainEvent
from shared.kernel.entities import Entity
from shared.kernel.exceptions import DomainException
from shared.kernel.result import Failure, Result, ResultAccessError, Success
from shared.kernel.value_objects import ValueObject

__all__ = [
    "AggregateRoot",
    "Clock",
    "DomainEvent",
    "DomainException",
    "Entity",
    "Failure",
    "Result",
    "ResultAccessError",
    "Success",
    "SystemClock",
    "ValueObject",
]
