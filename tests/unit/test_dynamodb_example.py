from __future__ import annotations

from shared.dynamodb.examples.dynamodb_example import put_temporary_item


class Table:
    def __init__(self) -> None:
        self.items: list[dict[str, object]] = []

    def put_item(self, *, Item: dict[str, object]) -> None:
        self.items.append(Item)


class Provider:
    def __init__(self) -> None:
        self.table = Table()

    def get_table(self) -> Table:
        return self.table


def test_dynamodb_example_adds_tenant_keys_metadata_and_ttl() -> None:
    provider = Provider()
    put_temporary_item(
        tenant_id="tenant-a",
        entity_id="entity-1",
        payload={"value": "safe"},
        table_provider=provider,  # type: ignore[arg-type]
    )
    item = provider.table.items[0]
    assert item["PK"] == "TENANT#tenant-a"
    assert item["SK"] == "ENTITY#entity-1"
    assert item["value"] == "safe"
    assert item["metadata"] == {"source": "example"}
    assert "ttl" in item
