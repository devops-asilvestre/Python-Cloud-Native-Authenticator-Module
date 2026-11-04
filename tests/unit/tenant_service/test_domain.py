import pytest

from tenant_service.domain.aggregates import Tenant
from tenant_service.domain.exceptions import InvalidTenantTransition
from tenant_service.domain.value_objects import (
    TenantCode,
    TenantDomain,
    TenantId,
    TenantMetadata,
    TenantName,
    TenantSettings,
    TenantSlug,
    TenantStatusValue,
)


def make_tenant() -> Tenant:
    return Tenant.create(
        TenantName("Acme Corporation"), TenantCode("acme"), TenantSlug("acme"),
        TenantSettings(), TenantMetadata({"plan": "standard"}), (TenantDomain("acme.com"),),
    )


def test_value_objects_normalize_and_validate() -> None:
    assert str(TenantName("  Acme  ")) == "Acme"
    assert str(TenantCode(" acme ")) == "ACME"
    assert str(TenantSlug("Acme-1")) == "acme-1"
    assert str(TenantDomain("ACME.COM")) == "acme.com"
    with pytest.raises(ValueError):
        TenantCode("ab")
    with pytest.raises(ValueError):
        TenantDomain("https://acme.com/path")


def test_tenant_lifecycle_and_events() -> None:
    tenant = make_tenant()
    assert tenant.tenant_status.value == TenantStatusValue.PENDING
    assert len(tenant.pull_events()) == 1
    tenant.activate()
    tenant.suspend()
    tenant.activate()
    tenant.deactivate()
    tenant.delete()
    events = tenant.pull_events()
    assert [event.event_type for event in events] == [
        "TenantActivated", "TenantSuspended", "TenantActivated",
        "TenantDeactivated", "TenantDeleted",
    ]
    assert str(tenant.tenant_status) == TenantStatusValue.DELETED


def test_invalid_transition_is_rejected() -> None:
    tenant = make_tenant()
    with pytest.raises(InvalidTenantTransition):
        tenant.suspend()


def test_delete_is_idempotent_and_status_values_are_validated() -> None:
    tenant = make_tenant()
    tenant.delete()
    tenant.delete()
    with pytest.raises(ValueError):
        from tenant_service.domain.value_objects import TenantStatus

        TenantStatus("UNKNOWN")  # type: ignore[arg-type]


def test_tenant_id_requires_uuidv7() -> None:
    with pytest.raises(ValueError):
        TenantId("00000000-0000-4000-8000-000000000000")


def test_settings_are_normalized_and_metadata_is_immutable() -> None:
    tenant = Tenant.create(
        TenantName("Acme Corporation"),
        TenantCode("ACME"),
        TenantSlug("acme"),
        TenantSettings(language="PT-BR", country="br", currency="brl"),
        TenantMetadata({"plan": "standard"}),
    )
    assert tenant.settings.language == "pt-br"
    assert tenant.settings.country == "BR"
    assert tenant.settings.currency == "BRL"
    with pytest.raises(TypeError):
        tenant.metadata.values["plan"] = "enterprise"  # type: ignore[index]
