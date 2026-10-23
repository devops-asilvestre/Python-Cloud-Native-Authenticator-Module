"""Semantic version for an event schema."""

from __future__ import annotations

import re
from functools import total_ordering

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictInt,
    model_serializer,
    model_validator,
)


@total_ordering
class EventVersion(BaseModel):
    """Immutable SemVer core version used to evolve event contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    major: StrictInt
    minor: StrictInt = 0
    patch: StrictInt = 0

    @model_validator(mode="before")
    @classmethod
    def parse_string_version(cls, value: object) -> object:
        if isinstance(value, str):
            if re.fullmatch(
                r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
                value,
            ) is None:
                raise ValueError(
                    f"Invalid event version: {value!r}. Expected major.minor.patch."
                )
            major, minor, patch = (int(component) for component in value.split("."))
            return {"major": major, "minor": minor, "patch": patch}
        return value

    @model_validator(mode="after")
    def validate_components(self) -> EventVersion:
        if self.major < 1:
            raise ValueError("Event major version must be at least 1.")
        if self.minor < 0 or self.patch < 0:
            raise ValueError("Event minor and patch versions cannot be negative.")
        return self

    @classmethod
    def parse(cls, value: str) -> EventVersion:
        """Parse a stable semantic version in ``major.minor.patch`` form."""

        if re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value) is None:
            raise ValueError(f"Invalid event version: {value!r}. Expected major.minor.patch.")
        major, minor, patch = (int(component) for component in value.split("."))
        return cls(major=major, minor=minor, patch=patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @model_serializer(mode="plain")
    def serialize_semver(self) -> str:
        return str(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, EventVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )
