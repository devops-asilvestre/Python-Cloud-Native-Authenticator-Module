"""Identity Directory foundation.

Revision ID: 20261103_002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261103_002"
down_revision: str | None = "20261103_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "identity_users",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("given_name", sa.String(100), nullable=False),
        sa.Column("family_name", sa.String(150), nullable=False),
        sa.Column("phone_number", sa.String(16), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, index=True),
        sa.Column("user_type", sa.String(30), nullable=False, index=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", name="uq_identity_users_tenant_email"),
    )


def downgrade() -> None:
    op.drop_table("identity_users")
