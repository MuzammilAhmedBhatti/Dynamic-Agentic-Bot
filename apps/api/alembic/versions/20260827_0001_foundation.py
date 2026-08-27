"""Create multi-tenant identity and RBAC foundation.

Revision ID: 20260827_0001
Revises: None
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260827_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

uuid_type = postgresql.UUID(as_uuid=True)


def _timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        *_timestamps(),
        sa.CheckConstraint("status IN ('active', 'suspended')", name="ck_organizations_status"),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_table(
        "users",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("identity_provider", sa.String(100), nullable=False),
        sa.Column("external_subject", sa.String(255), nullable=False),
        sa.Column("email_normalized", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(200)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint(
            "identity_provider", "external_subject", name="uq_users_identity"
        ),
    )
    op.create_index("ix_users_email_normalized", "users", ["email_normalized"])
    op.create_table(
        "organization_memberships",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column(
            "organization_id",
            uuid_type,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            uuid_type,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        *_timestamps(),
        sa.CheckConstraint("status IN ('active', 'suspended')", name="ck_memberships_status"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
        sa.UniqueConstraint("id", "organization_id", name="uq_membership_id_org"),
    )
    op.create_index(
        "ix_memberships_user_status", "organization_memberships", ["user_id", "status"]
    )
    op.create_table(
        "roles",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column(
            "organization_id",
            uuid_type,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500)),
        *_timestamps(),
        sa.UniqueConstraint("organization_id", "name", name="uq_roles_org_name"),
        sa.UniqueConstraint("id", "organization_id", name="uq_roles_id_org"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("code", sa.String(150), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_table(
        "membership_roles",
        sa.Column("membership_id", uuid_type, primary_key=True),
        sa.Column("role_id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.ForeignKeyConstraint(
            ["membership_id", "organization_id"],
            ["organization_memberships.id", "organization_memberships.organization_id"],
            ondelete="CASCADE",
            name="fk_membership_roles_membership_org",
        ),
        sa.ForeignKeyConstraint(
            ["role_id", "organization_id"],
            ["roles.id", "roles.organization_id"],
            ondelete="CASCADE",
            name="fk_membership_roles_role_org",
        ),
    )
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            uuid_type,
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            uuid_type,
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("membership_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_index("ix_memberships_user_status", table_name="organization_memberships")
    op.drop_table("organization_memberships")
    op.drop_index("ix_users_email_normalized", table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")
