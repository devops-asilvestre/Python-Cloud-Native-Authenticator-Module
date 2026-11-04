"""Normalize and validate secret names according to AWS-friendly rules."""

from __future__ import annotations

import re


class SecretNamingConvention:
    """Reusable rules for constructing and validating secret names."""

    _PATTERN = re.compile(r"^[A-Za-z0-9/_+=.@-]+$")

    @staticmethod
    def normalize(name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("Secret name must be provided as a string.")
        value = name.strip().replace('\\', '/')
        while '//' in value:
            value = value.replace('//', '/')
        return value

    def is_valid(self, name: str) -> bool:
        return bool(name) and bool(self._PATTERN.fullmatch(self.normalize(name)))

    def build(self, *parts: str) -> str:
        normalized = [self.normalize(part) for part in parts if part]
        return "/".join(normalized)
