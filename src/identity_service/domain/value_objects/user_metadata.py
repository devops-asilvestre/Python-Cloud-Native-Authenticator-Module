from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

type MetadataValue = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class UserMetadata:
    values: dict[str, MetadataValue]

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", dict(self.values))

    def __iter__(self) -> Iterator[tuple[str, MetadataValue]]:
        return iter(self.values.items())
