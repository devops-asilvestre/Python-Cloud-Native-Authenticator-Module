"""Create tenant aggregate storage.

Revision ID: 20261103_001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261103_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("tenant_id", sa.String(36), primary_key=True),
        sa.Column("tenant_name", sa.String(200), nullable=False),
        sa.Column("tenant_code", sa.String(20), nullable=False),
        sa.Column("tenant_slug", sa.String(100), nullable=False),
        sa.Column("tenant_status", sa.String(20), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("domains", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_code"),
        sa.UniqueConstraint("tenant_slug"),
    )
    op.create_index("ix_tenants_tenant_code", "tenants", ["tenant_code"])
    op.create_index("ix_tenants_tenant_slug", "tenants", ["tenant_slug"])
    op.create_index("ix_tenants_tenant_status", "tenants", ["tenant_status"])


def downgrade() -> None:
    op.drop_index("ix_tenants_tenant_status", table_name="tenants")
    op.drop_index("ix_tenants_tenant_slug", table_name="tenants")
    op.drop_index("ix_tenants_tenant_code", table_name="tenants")
    op.drop_table("tenants")
