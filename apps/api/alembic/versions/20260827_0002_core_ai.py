"""Create the Milestone 2 knowledge, ingestion, and trace schema.

Revision ID: 20260827_0002
Revises: 20260827_0001
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260827_0002"
down_revision: str | Sequence[str] | None = "20260827_0001"
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
        "knowledge_bases",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column(
            "organization_id",
            uuid_type,
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        *_timestamps(),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_knowledge_bases_status"),
        sa.UniqueConstraint("organization_id", "name", name="uq_knowledge_bases_org_name"),
        sa.UniqueConstraint("id", "organization_id", name="uq_knowledge_bases_id_org"),
    )
    op.create_index(
        "ix_knowledge_bases_org_status", "knowledge_bases", ["organization_id", "status"]
    )
    op.create_table(
        "documents",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("knowledge_base_id", uuid_type, nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_checksum", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("page_count", sa.Integer()),
        sa.Column("status", sa.String(30), nullable=False, server_default="queued"),
        sa.Column("error_code", sa.String(100)),
        sa.Column("source_object_ref", sa.String(1000), nullable=False),
        sa.Column("ingestion_version", sa.String(100), nullable=False),
        sa.Column("embedding_model", sa.String(200)),
        sa.Column("embedding_dimension", sa.Integer()),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_documents_kb_org",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'ready', 'ocr_required', 'failed')",
            name="ck_documents_status",
        ),
        sa.UniqueConstraint(
            "organization_id", "knowledge_base_id", "content_checksum",
            name="uq_documents_org_kb_checksum",
        ),
        sa.UniqueConstraint("id", "organization_id", name="uq_documents_id_org"),
        sa.UniqueConstraint(
            "id", "organization_id", "knowledge_base_id", name="uq_documents_id_org_kb"
        ),
    )
    op.create_index(
        "ix_documents_org_kb_status",
        "documents",
        ["organization_id", "knowledge_base_id", "status"],
    )
    op.create_table(
        "document_pages",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("document_id", uuid_type, nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("text_object_ref", sa.String(1000), nullable=False),
        sa.Column("preview_object_ref", sa.String(1000), nullable=False),
        sa.Column("text_checksum", sa.String(64), nullable=False),
        sa.Column("extracted_character_count", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["document_id", "organization_id"],
            ["documents.id", "documents.organization_id"],
            ondelete="CASCADE",
            name="fk_document_pages_document_org",
        ),
        sa.CheckConstraint("page_number > 0", name="ck_document_pages_number"),
        sa.UniqueConstraint("document_id", "page_number", name="uq_document_pages_number"),
        sa.UniqueConstraint("id", "organization_id", name="uq_document_pages_id_org"),
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("knowledge_base_id", uuid_type, nullable=False),
        sa.Column("document_id", uuid_type, nullable=False),
        sa.Column("page_id", uuid_type, nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("text_object_ref", sa.String(1000), nullable=False),
        sa.Column("content_checksum", sa.String(64), nullable=False),
        sa.Column("section", sa.String(300)),
        sa.Column("title", sa.String(300)),
        sa.Column("chunker_version", sa.String(100), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("chunk_overlap", sa.Integer(), nullable=False),
        sa.Column("vector_id", sa.String(100), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["document_id", "organization_id", "knowledge_base_id"],
            ["documents.id", "documents.organization_id", "documents.knowledge_base_id"],
            ondelete="CASCADE",
            name="fk_document_chunks_document_org_kb",
        ),
        sa.ForeignKeyConstraint(
            ["page_id", "organization_id"],
            ["document_pages.id", "document_pages.organization_id"],
            ondelete="CASCADE",
            name="fk_document_chunks_page_org",
        ),
        sa.UniqueConstraint("document_id", "ordinal", name="uq_document_chunks_ordinal"),
        sa.UniqueConstraint("vector_id", name="uq_document_chunks_vector_id"),
    )
    op.create_index(
        "ix_document_chunks_org_kb_doc",
        "document_chunks",
        ["organization_id", "knowledge_base_id", "document_id"],
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column(
            "user_id", uuid_type, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("knowledge_base_id", uuid_type, nullable=False),
        sa.Column("trace_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("graph_version", sa.String(100), nullable=False),
        sa.Column("prompt_version", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(100)),
        sa.Column("model", sa.String(200)),
        sa.Column("error_code", sa.String(100)),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_agent_runs_kb_org",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_agent_runs_status",
        ),
        sa.UniqueConstraint("trace_id", name="uq_agent_runs_trace_id"),
    )
    op.create_index(
        "ix_agent_runs_org_user", "agent_runs", ["organization_id", "user_id", "created_at"]
    )
    op.create_table(
        "agent_trace_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "run_id", uuid_type, sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("stage", sa.String(100), nullable=False),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column(
            "safe_summary", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "sequence", name="uq_agent_trace_events_sequence"),
    )
    op.create_index(
        "ix_agent_trace_events_run_sequence", "agent_trace_events", ["run_id", "sequence"]
    )


def downgrade() -> None:
    op.drop_index("ix_agent_trace_events_run_sequence", table_name="agent_trace_events")
    op.drop_table("agent_trace_events")
    op.drop_index("ix_agent_runs_org_user", table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index("ix_document_chunks_org_kb_doc", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("document_pages")
    op.drop_index("ix_documents_org_kb_status", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_knowledge_bases_org_status", table_name="knowledge_bases")
    op.drop_table("knowledge_bases")
