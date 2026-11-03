from __future__ import annotations

import re
from dataclasses import dataclass

from authentication_service.domain.exceptions import InvalidPassword


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    minimum_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True

    def validate(self, password: str) -> None:
        failures: list[str] = []
        if len(password) < self.minimum_length:
            failures.append(f"at least {self.minimum_length} characters")
        if self.require_uppercase and re.search(r"[A-Z]", password) is None:
            failures.append("an uppercase character")
        if self.require_lowercase and re.search(r"[a-z]", password) is None:
            failures.append("a lowercase character")
        if self.require_digit and re.search(r"\d", password) is None:
            failures.append("a digit")
        if self.require_special and re.search(r"[^A-Za-z0-9]", password) is None:
            failures.append("a special character")
        if failures:
            raise InvalidPassword("Password must contain " + ", ".join(failures) + ".")
