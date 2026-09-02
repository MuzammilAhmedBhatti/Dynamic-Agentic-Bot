"""Add automatic organization-wide knowledge-base search scope.

Revision ID: 20260902_0005
Revises: 20260828_0004
Create Date: 2026-09-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_0005"
down_revision: str | Sequence[str] | None = "20260828_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "agent_runs",
        sa.Column(
            "search_all_knowledge_bases",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_runs", "search_all_knowledge_bases")
