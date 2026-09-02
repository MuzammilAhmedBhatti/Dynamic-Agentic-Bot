from __future__ import annotations

import uuid
from datetime import datetime
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
    knowledge_base_id: uuid.UUID | None = None
    search_all_knowledge_bases: bool = False
    persona_id: uuid.UUID | None = None
    provider: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=200)
    data_source_id: uuid.UUID | None = None


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


class PersonaResponse(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str
    allowed_routes: list[str]
    default_provider: str
    default_model: str
    scope: str
    is_active: bool


class ProviderModelResponse(BaseModel):
    provider: str
    model: str
    available: bool
    reason: str | None = None


class CalculationResponse(BaseModel):
    operation: str
    inputs: list[float]
    result: float
    unit: str | None = None


class DatabaseEvidenceResponse(BaseModel):
    source_id: uuid.UUID
    database_name: str
    tables: list[str]
    columns: list[str]
    row_count: int


class DataSourceCreate(BaseModel):
    knowledge_base_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    kind: Literal["postgresql"] = "postgresql"
    connection_url: str = Field(min_length=1, max_length=2000)
    allowed_schema: str = Field(min_length=1, max_length=100)
    allowed_tables: list[str] = Field(min_length=1, max_length=50)


class DataSourceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    knowledge_base_id: uuid.UUID
    name: str
    kind: str
    allowed_schema: str
    allowed_tables: list[str]
    is_active: bool


class ChatRunResponse(BaseModel):
    run_id: uuid.UUID
    trace_id: str
    answer: str
    support: Literal["grounded", "unanswerable"]
    persona: PersonaResponse
    route: list[str]
    sources: list[CitationSourceResponse]
    provider: str | None
    model: str | None
    graph_version: str
    prompt_version: str
    calculations: list[CalculationResponse] = Field(default_factory=list)
    database_evidence: list[DatabaseEvidenceResponse] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class TestSessionRequest(BaseModel):
    user_id: uuid.UUID


class TestSessionResponse(BaseModel):
    authenticated: Literal[True] = True
    user_id: uuid.UUID


LabType = Literal["data", "classical_ml", "deep_learning", "nlp", "transformer"]


class LabExperimentCreate(BaseModel):
    lab_type: LabType
    algorithm: str = Field(min_length=1, max_length=100)
    dataset: str = Field(default="builtin", min_length=1, max_length=200)
    parameters: dict[str, object] = Field(default_factory=dict)
    random_seed: int = Field(default=42, ge=0, le=2_147_483_647)


class EvaluationRunCreate(BaseModel):
    benchmark: Literal[
        "rag",
        "rag_comparison",
        "persona_router",
        "database",
        "math",
        "security",
        "llm",
        "prompts",
    ]
    parameters: dict[str, object] = Field(default_factory=dict)
    random_seed: int = Field(default=42, ge=0, le=2_147_483_647)


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    lab_type: str
    algorithm: str
    dataset: str
    dataset_version: str
    parameters: dict[str, object]
    metrics: dict[str, object]
    artifact_metadata: dict[str, object]
    library_versions: dict[str, object]
    random_seed: int
    status: str
    duration_ms: int | None
    started_at: datetime | None
    completed_at: datetime | None
    error_code: str | None
    created_at: datetime


class LabCatalogResponse(BaseModel):
    algorithms: dict[str, list[str]]
    datasets: list[str]
    limits: dict[str, int | float]
