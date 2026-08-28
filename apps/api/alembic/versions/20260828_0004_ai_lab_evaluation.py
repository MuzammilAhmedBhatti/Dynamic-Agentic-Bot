"""Add tenant-scoped AI Lab and evaluation experiments.

Revision ID: 20260828_0004
Revises: 20260828_0003
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260828_0004"
down_revision: str | Sequence[str] | None = "20260828_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid_type = postgresql.UUID(as_uuid=True)
    op.create_table(
        "experiments",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column(
            "organization_id",
            uuid_type,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", uuid_type, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("lab_type", sa.String(50), nullable=False),
        sa.Column("algorithm", sa.String(100), nullable=False),
        sa.Column("dataset", sa.String(200), nullable=False),
        sa.Column("dataset_version", sa.String(100), nullable=False),
        sa.Column("parameters", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("metrics", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("artifact_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("library_versions", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("random_seed", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_code", sa.String(100)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_experiments_status",
        ),
        sa.CheckConstraint(
            "lab_type IN ('data', 'classical_ml', 'deep_learning', 'nlp', "
            "'transformer', 'rag_evaluation', 'agent_evaluation', 'security_evaluation')",
            name="ck_experiments_lab_type",
        ),
    )
    op.create_index(
        "ix_experiments_org_created", "experiments", ["organization_id", "created_at"]
    )
    op.create_index(
        "ix_experiments_org_status", "experiments", ["organization_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_experiments_org_status", table_name="experiments")
    op.drop_index("ix_experiments_org_created", table_name="experiments")
    op.drop_table("experiments")
