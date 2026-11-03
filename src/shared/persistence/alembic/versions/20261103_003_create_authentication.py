"""Authentication foundation.

Revision ID: 20261103_003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261103_003"
down_revision: str | None = "20261103_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "authentication_credentials",
        sa.Column("credential_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", name="uq_auth_credentials_tenant_email"),
    )
    op.create_index("ix_auth_credentials_tenant", "authentication_credentials", ["tenant_id"])
    op.create_table(
        "authentication_sessions",
        sa.Column("session_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("ip_address", sa.String(64)),
    )
    op.create_index("ix_auth_sessions_tenant", "authentication_sessions", ["tenant_id"])
    op.create_table(
        "authentication_audit",
        sa.Column("audit_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("event_id", sa.String(36), nullable=False, unique=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("user_id", sa.String(36)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(100)),
        sa.Column("source", sa.String(100), nullable=False),
    )
    op.create_index("ix_auth_audit_tenant", "authentication_audit", ["tenant_id"])
    op.create_index("ix_auth_audit_event_type", "authentication_audit", ["event_type"])


def downgrade() -> None:
    op.drop_table("authentication_audit")
    op.drop_table("authentication_sessions")
    op.drop_table("authentication_credentials")
