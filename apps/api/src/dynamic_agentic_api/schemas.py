from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"
    database: Literal["ready"] = "ready"


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str


class TenantContextResponse(BaseModel):
    organization: OrganizationResponse
    user_id: uuid.UUID
    membership_id: uuid.UUID
    roles: list[str]
    permissions: list[str]


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("name cannot be blank")
        return normalized


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    status: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    knowledge_base_id: uuid.UUID
    filename: str
    mime_type: str
    size_bytes: int
    page_count: int | None
    status: str
    error_code: str | None
    ingestion_version: str
    embedding_model: str | None


class ChatRunCreate(BaseModel):
    knowledge_base_id: uuid.UUID


class ChatRunCreated(BaseModel):
    run_id: uuid.UUID
    trace_id: str
    status: str


class ChatRunExecute(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class CitationSourceResponse(BaseModel):
    document_id: uuid.UUID
    document_name: str
    page_number: int
    chunk_id: uuid.UUID
    preview_reference: str


class ChatRunResponse(BaseModel):
    run_id: uuid.UUID
    trace_id: str
    answer: str
    support: Literal["grounded", "unanswerable"]
    sources: list[CitationSourceResponse]
    provider: str | None
    model: str | None
    graph_version: str
    prompt_version: str


class TestSessionRequest(BaseModel):
    user_id: uuid.UUID


class TestSessionResponse(BaseModel):
    authenticated: Literal[True] = True
    user_id: uuid.UUID
