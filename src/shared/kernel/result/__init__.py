"""Explicit success-or-failure values."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ResultAccessError(TypeError):
    """Raised when a caller reads the value from the wrong Result variant."""


class Result[T, E](ABC):
    """Base for a successful value or an explicit error value."""

    @classmethod
    def success(cls, value: T) -> Result[T, E]:
        return Success(value)

    @classmethod
    def failure(cls, error: E) -> Result[T, E]:
        return Failure(error)

    @property
    @abstractmethod
    def is_success(self) -> bool: ...

    @property
    def is_failure(self) -> bool:
        return not self.is_success

    @property
    @abstractmethod
    def value(self) -> T: ...

    @property
    @abstractmethod
    def error(self) -> E: ...


class Success[T, E](Result[T, E]):
    """Successful Result variant."""

    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def is_success(self) -> bool:
        return True

    @property
    def value(self) -> T:
        return self._value

    @property
    def error(self) -> E:
        raise ResultAccessError("A successful Result has no error.")


class Failure[T, E](Result[T, E]):
    """Failed Result variant."""

    __slots__ = ("_error",)

    def __init__(self, error: E) -> None:
        self._error = error

    @property
    def is_success(self) -> bool:
        return False

    @property
    def value(self) -> T:
        raise ResultAccessError("A failed Result has no value.")

    @property
    def error(self) -> E:
        return self._error
