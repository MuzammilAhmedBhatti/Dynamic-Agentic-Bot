from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dynamic_agentic_api.db.base import Base, TimestampMixin


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended')", name="ck_organizations_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    roles: Mapped[list[Role]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("identity_provider", "external_subject", name="uq_users_identity"),
        Index("ix_users_email_normalized", "email_normalized"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identity_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    external_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email_normalized: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    memberships: Mapped[list[OrganizationMembership]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class OrganizationMembership(TimestampMixin, Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
        UniqueConstraint("id", "organization_id", name="uq_membership_id_org"),
        CheckConstraint("status IN ('active', 'suspended')", name="ck_memberships_status"),
        Index("ix_memberships_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    organization: Mapped[Organization] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")
    roles: Mapped[list[Role]] = relationship(
        secondary="membership_roles", back_populates="memberships", viewonly=True
    )


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_roles_org_name"),
        UniqueConstraint("id", "organization_id", name="uq_roles_id_org"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    organization: Mapped[Organization] = relationship(back_populates="roles")
    memberships: Mapped[list[OrganizationMembership]] = relationship(
        secondary="membership_roles", back_populates="roles", viewonly=True
    )
    permissions: Mapped[list[Permission]] = relationship(
        secondary="role_permissions", back_populates="roles", viewonly=True
    )


class Permission(TimestampMixin, Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    roles: Mapped[list[Role]] = relationship(
        secondary="role_permissions", back_populates="permissions", viewonly=True
    )


class MembershipRole(Base):
    __tablename__ = "membership_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["membership_id", "organization_id"],
            ["organization_memberships.id", "organization_memberships.organization_id"],
            ondelete="CASCADE",
            name="fk_membership_roles_membership_org",
        ),
        ForeignKeyConstraint(
            ["role_id", "organization_id"],
            ["roles.id", "roles.organization_id"],
            ondelete="CASCADE",
            name="fk_membership_roles_role_org",
        ),
    )

    membership_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )


class KnowledgeBase(TimestampMixin, Base):
    __tablename__ = "knowledge_bases"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_knowledge_bases_org_name"),
        UniqueConstraint("id", "organization_id", name="uq_knowledge_bases_id_org"),
        CheckConstraint("status IN ('active', 'archived')", name="ck_knowledge_bases_status"),
        Index("ix_knowledge_bases_org_status", "organization_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class Persona(TimestampMixin, Base):
    __tablename__ = "personas"
    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_personas_org_slug"),
        CheckConstraint("scope IN ('system', 'tenant')", name="ck_personas_scope"),
        Index("ix_personas_org_active", "organization_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    system_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    allowed_routes: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    default_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    default_model: Mapped[str] = mapped_column(String(200), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="system")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)


class DataSource(TimestampMixin, Base):
    __tablename__ = "data_sources"
    __table_args__ = (
        ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_data_sources_kb_org",
        ),
        UniqueConstraint("organization_id", "name", name="uq_data_sources_org_name"),
        UniqueConstraint("id", "organization_id", name="uq_data_sources_id_org"),
        CheckConstraint("kind IN ('postgresql')", name="ck_data_sources_kind"),
        Index("ix_data_sources_org_kb_active", "organization_id", "knowledge_base_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False, default="postgresql")
    encrypted_connection: Mapped[str] = mapped_column(Text, nullable=False)
    allowed_schema: Mapped[str] = mapped_column(String(100), nullable=False)
    allowed_tables: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)


class Document(TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_documents_kb_org",
        ),
        UniqueConstraint(
            "organization_id",
            "knowledge_base_id",
            "content_checksum",
            name="uq_documents_org_kb_checksum",
        ),
        UniqueConstraint("id", "organization_id", name="uq_documents_id_org"),
        UniqueConstraint(
            "id", "organization_id", "knowledge_base_id", name="uq_documents_id_org_kb"
        ),
        CheckConstraint(
            "status IN ('queued', 'processing', 'ready', 'ocr_required', 'failed')",
            name="ck_documents_status",
        ),
        Index("ix_documents_org_kb_status", "organization_id", "knowledge_base_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued")
    error_code: Mapped[str | None] = mapped_column(String(100))
    source_object_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    ingestion_version: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_model: Mapped[str | None] = mapped_column(String(200))
    embedding_dimension: Mapped[int | None] = mapped_column(Integer)


class DocumentPage(TimestampMixin, Base):
    __tablename__ = "document_pages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["document_id", "organization_id"],
            ["documents.id", "documents.organization_id"],
            ondelete="CASCADE",
            name="fk_document_pages_document_org",
        ),
        UniqueConstraint("document_id", "page_number", name="uq_document_pages_number"),
        UniqueConstraint("id", "organization_id", name="uq_document_pages_id_org"),
        CheckConstraint("page_number > 0", name="ck_document_pages_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text_object_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    preview_object_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    text_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    extracted_character_count: Mapped[int] = mapped_column(Integer, nullable=False)


class DocumentChunk(TimestampMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["document_id", "organization_id", "knowledge_base_id"],
            ["documents.id", "documents.organization_id", "documents.knowledge_base_id"],
            ondelete="CASCADE",
            name="fk_document_chunks_document_org_kb",
        ),
        ForeignKeyConstraint(
            ["page_id", "organization_id"],
            ["document_pages.id", "document_pages.organization_id"],
            ondelete="CASCADE",
            name="fk_document_chunks_page_org",
        ),
        UniqueConstraint("document_id", "ordinal", name="uq_document_chunks_ordinal"),
        Index(
            "ix_document_chunks_org_kb_doc", "organization_id", "knowledge_base_id", "document_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    page_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    text_object_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    section: Mapped[str | None] = mapped_column(String(300))
    title: Mapped[str | None] = mapped_column(String(300))
    chunker_version: Mapped[str] = mapped_column(String(100), nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class AgentRun(TimestampMixin, Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["knowledge_base_id", "organization_id"],
            ["knowledge_bases.id", "knowledge_bases.organization_id"],
            ondelete="CASCADE",
            name="fk_agent_runs_kb_org",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed')",
            name="ck_agent_runs_status",
        ),
        Index("ix_agent_runs_org_user", "organization_id", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    graph_version: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(200))
    persona_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    data_source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    route: Mapped[str | None] = mapped_column(String(100))
    error_code: Mapped[str | None] = mapped_column(String(100))


class AgentTraceEvent(Base):
    __tablename__ = "agent_trace_events"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_agent_trace_events_sequence"),
        Index("ix_agent_trace_events_run_sequence", "run_id", "sequence"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
