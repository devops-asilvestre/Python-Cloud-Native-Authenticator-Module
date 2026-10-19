from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVICE_CONTEXTS = (
    "tenant-service",
    "identity-directory-service",
    "authentication-service",
    "authorization-service",
    "protocol-service",
    "audit-service",
)
REQUIRED_DIRECTORIES = (
    "services",
    "shared/kernel",
    "shared/events",
    "shared/observability",
    "shared/security",
    "infrastructure/docker",
    "infrastructure/terraform",
    "infrastructure/environments",
    "infrastructure/scripts",
    "docs/architecture",
    "docs/adrs",
    "docs/user-stories",
    "docs/security",
    "docs/operations",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "tests/contract",
    "tests/architecture",
    "tools",
)


def test_required_workspace_directories_exist() -> None:
    for directory in REQUIRED_DIRECTORIES:
        assert (ROOT / directory).is_dir(), directory


def test_each_bounded_context_has_a_readme() -> None:
    for service in SERVICE_CONTEXTS:
        readme = ROOT / "services" / service / "README.md"
        assert readme.is_file(), service
        assert readme.read_text(encoding="utf-8").startswith("# "), service


def test_shared_components_have_documented_boundaries() -> None:
    for component in ("kernel", "events", "observability", "security"):
        readme = ROOT / "shared" / component / "README.md"
        assert readme.is_file(), component
        assert readme.read_text(encoding="utf-8").strip(), component
