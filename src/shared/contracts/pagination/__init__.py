"""Generic pagination response."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PaginationResponse[T]:
    """A page of values and its position in the complete result set."""

    items: tuple[T, ...]
    page: int
    page_size: int
    total_items: int

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Page must be at least 1.")
        if self.page_size < 1:
            raise ValueError("Page size must be at least 1.")
        if self.total_items < 0:
            raise ValueError("Total items cannot be negative.")

    @property
    def total_pages(self) -> int:
        return (self.total_items + self.page_size - 1) // self.page_size
