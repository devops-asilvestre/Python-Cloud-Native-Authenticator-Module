from datetime import UTC

import pytest

from shared.contracts.pagination import PaginationResponse
from shared.contracts.responses import BaseResponse, ErrorResponse
from shared.events.metadata import EventMetadata
from shared.events.versioning import EventVersion


def test_response_envelopes_keep_explicit_data_and_error_fields() -> None:
    assert BaseResponse(data={"id": "one"}).data == {"id": "one"}
    assert ErrorResponse(code="not_found", message="Not found").code == "not_found"


def test_pagination_response_validates_and_calculates_total_pages() -> None:
    response = PaginationResponse(items=("a", "b"), page=1, page_size=2, total_items=3)

    assert response.total_pages == 2
    with pytest.raises(ValueError, match="Page must"):
        PaginationResponse(items=(), page=0, page_size=2, total_items=0)


def test_event_metadata_uses_utc_and_version_is_validated() -> None:
    assert EventMetadata().occurred_at.tzinfo == UTC
    assert EventVersion(major=1, minor=2) < EventVersion(major=2)
    with pytest.raises(ValueError, match="major version"):
        EventVersion(major=0)
