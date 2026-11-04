"""Small usage example for shared-kernel value and result contracts."""

from dataclasses import dataclass

from shared.kernel import Result, ValueObject


@dataclass(frozen=True, slots=True)
class EmailAddress(ValueObject):
    address: str

    @property
    def value(self) -> str:
        return self.address


def create_address(address: str) -> Result[EmailAddress, str]:
    if "@" not in address:
        return Result.failure("invalid_address")
    return Result.success(EmailAddress(address))


if __name__ == "__main__":
    result = create_address("person@example.test")
    if result.is_success:
        print(result.value)
