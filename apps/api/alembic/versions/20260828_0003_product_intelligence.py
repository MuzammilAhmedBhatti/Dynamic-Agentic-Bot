"""Add Milestone 3 personas, structured sources, and run selections.

Revision ID: 20260828_0003
Revises: 20260827_0002
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260828_0003"
down_revision: str | Sequence[str] | None = "20260827_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

uuid_type = postgresql.UUID(as_uuid=True)


def _timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS demo_business")
    op.execute(
        "CREATE TABLE demo_business.customers (id integer PRIMARY KEY, name text NOT NULL, signed_up_on date NOT NULL)"
    )
    op.execute(
        "CREATE TABLE demo_business.orders (id integer PRIMARY KEY, customer_id integer NOT NULL REFERENCES demo_business.customers(id), ordered_on date NOT NULL, amount numeric(12,2) NOT NULL)"
    )
    op.execute(
        "CREATE TABLE demo_business.sales (id integer PRIMARY KEY, sold_on date NOT NULL, region text NOT NULL, amount numeric(12,2) NOT NULL)"
    )
    op.execute(
        "INSERT INTO demo_business.customers VALUES (1, 'Acme North', '2026-08-02'), (2, 'Cedar Labs', '2026-08-11'), (3, 'Harbor Retail', '2026-07-20')"
    )
    op.execute(
        "INSERT INTO demo_business.orders VALUES (1, 1, '2026-08-03', 120.00), (2, 1, '2026-08-14', 180.00), (3, 2, '2026-08-16', 300.00), (4, 3, '2026-07-25', 200.00)"
    )
    op.execute(
        "INSERT INTO demo_business.sales VALUES (1, '2026-06-01', 'North', 4200.00), (2, '2026-07-01', 'South', 5100.00), (3, '2026-08-01', 'North', 5700.00)"
    )
    op.create_table(
        "personas",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("system_behavior", sa.Text(), nullable=False),
        sa.Column("allowed_routes", postgresql.JSONB(), nullable=False),
        sa.Column("default_provider", sa.String(100), nullable=False),
        sa.Column("default_model", sa.String(200), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False, server_default="system"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.CheckConstraint("scope IN ('system', 'tenant')", name="ck_personas_scope"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_personas_org_slug"),
    )
    op.create_index("ix_personas_org_active", "personas", ["organization_id", "is_active"])
    op.create_table(
        "data_sources",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("knowledge_base_id", uuid_type, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False, server_default="postgresql"),
        sa.Column("encrypted_connection", sa.Text(), nullable=False),
        sa.Column("allowed_schema", sa.String(100), nullable=False),
        sa.Column("allowed_tables", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_data_sources_kb_org",
        ),
        sa.CheckConstraint("kind IN ('postgresql')", name="ck_data_sources_kind"),
        sa.UniqueConstraint("organization_id", "name", name="uq_data_sources_org_name"),
        sa.UniqueConstraint("id", "organization_id", name="uq_data_sources_id_org"),
    )
    op.create_index(
        "ix_data_sources_org_kb_active",
        "data_sources",
        ["organization_id", "knowledge_base_id", "is_active"],
    )
    op.add_column("agent_runs", sa.Column("persona_id", uuid_type))
    op.add_column("agent_runs", sa.Column("data_source_id", uuid_type))
    op.add_column("agent_runs", sa.Column("route", sa.String(100)))


def downgrade() -> None:
    op.drop_column("agent_runs", "route")
    op.drop_column("agent_runs", "data_source_id")
    op.drop_column("agent_runs", "persona_id")
    op.drop_index("ix_data_sources_org_kb_active", table_name="data_sources")
    op.drop_table("data_sources")
    op.drop_index("ix_personas_org_active", table_name="personas")
    op.drop_table("personas")
    op.execute("DROP SCHEMA IF EXISTS demo_business CASCADE")
