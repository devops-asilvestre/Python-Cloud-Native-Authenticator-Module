"""Value-based immutable object abstraction."""

from abc import ABC, abstractmethod


class ValueObject(ABC):
    """Base for immutable values that compare by their declared value."""

    @property
    @abstractmethod
    def value(self) -> object:
        """Return the complete value used for equality and hashing."""

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self), self.value))
