from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.db.models import Document, DocumentChunk
from dynamic_agentic_api.embeddings.providers import EmbeddingProvider
from dynamic_agentic_api.llm.gateway import EvidenceBlock, LlmProvider, LlmRequest
from dynamic_agentic_api.storage.service import StorageService
from dynamic_agentic_api.vector_store.service import VectorStore

UNANSWERABLE = "I cannot answer that from the available knowledge."


@dataclass(frozen=True, slots=True)
class CitationSource:
    document_id: uuid.UUID
    document_name: str
    page_number: int
    chunk_id: uuid.UUID
    preview_reference: str


@dataclass(frozen=True, slots=True)
class RagResult:
    answer: str
    sources: list[CitationSource]
    support: Literal["grounded", "unanswerable"]
    provider: str | None
    model: str | None
    prompt_version: str
    retrieval_count: int


class RagService:
    prompt_version = "grounded-rag-v1"

    def __init__(
        self,
        *,
        settings: Settings,
        storage: StorageService,
        embeddings: EmbeddingProvider,
        vectors: VectorStore,
        llm: LlmProvider,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._embeddings = embeddings
        self._vectors = vectors
        self._llm = llm

    async def answer(
        self,
        *,
        session: AsyncSession,
        context: TenantContext,
        knowledge_base_id: uuid.UUID,
        question: str,
        trace: Callable[[str, str, dict[str, object]], Awaitable[None]] | None = None,
    ) -> RagResult:
        if trace:
            await trace("retrieval_started", "document_retrieval", {})
        query_result = await self._embeddings.embed_query(question)
        matches = await self._vectors.query(
            namespace=str(context.organization_id),
            vector=query_result.vectors[0],
            top_k=self._settings.rag_top_k,
            filters={
                "tenant_id": str(context.organization_id),
                "knowledge_base_id": str(knowledge_base_id),
            },
        )
        if trace:
            await trace(
                "retrieval_completed",
                "document_retrieval",
                {"candidate_count": len(matches)},
            )
        chunk_ids = [_metadata_uuid(match.metadata, "chunk_id") for match in matches]
        chunk_ids = [item for item in chunk_ids if item is not None]
        if not chunk_ids:
            return self._unanswerable(retrieval_count=0)

        statement = (
            select(DocumentChunk, Document)
            .join(
                Document,
                (Document.id == DocumentChunk.document_id)
                & (Document.organization_id == DocumentChunk.organization_id)
                & (Document.knowledge_base_id == DocumentChunk.knowledge_base_id),
            )
            .where(
                DocumentChunk.id.in_(chunk_ids),
                DocumentChunk.organization_id == context.organization_id,
                DocumentChunk.knowledge_base_id == knowledge_base_id,
                Document.organization_id == context.organization_id,
                Document.knowledge_base_id == knowledge_base_id,
                Document.status == "ready",
            )
        )
        authorized_rows = (await session.execute(statement)).all()
        by_id = {chunk.id: (chunk, document) for chunk, document in authorized_rows}
        evidence: list[EvidenceBlock] = []
        source_by_id: dict[str, CitationSource] = {}
        used_chars = 0
        for chunk_id in chunk_ids:
            pair = by_id.get(chunk_id)
            if pair is None:
                continue
            chunk, document = pair
            text = (await self._storage.read(chunk.text_object_ref)).decode(
                "utf-8", errors="replace"
            )
            remaining = self._settings.rag_context_max_chars - used_chars
            if remaining <= 0:
                break
            text = text[:remaining]
            used_chars += len(text)
            evidence.append(
                EvidenceBlock(
                    chunk_id=str(chunk.id),
                    document_name=document.filename,
                    page_number=chunk.page_number,
                    text=text,
                )
            )
            source_by_id[str(chunk.id)] = CitationSource(
                document_id=document.id,
                document_name=document.filename,
                page_number=chunk.page_number,
                chunk_id=chunk.id,
                preview_reference=(
                    f"/api/v1/organizations/{context.organization_id}/documents/"
                    f"{document.id}/pages/{chunk.page_number}/preview"
                ),
            )
        if not evidence:
            return self._unanswerable(retrieval_count=len(matches))

        if trace:
            await trace("llm_started", "grounded_generation", {})
        generated = await self._llm.generate_grounded_answer(
            LlmRequest(
                question=question,
                evidence=evidence,
                prompt_version=self.prompt_version,
            )
        )
        if trace:
            await trace(
                "llm_completed",
                "grounded_generation",
                {"provider": generated.provider, "model": generated.model},
            )
        cited = list(dict.fromkeys(generated.cited_chunk_ids))
        if (
            generated.insufficient_evidence
            or not cited
            or any(item not in source_by_id for item in cited)
        ):
            return RagResult(
                answer=UNANSWERABLE,
                sources=[],
                support="unanswerable",
                provider=generated.provider,
                model=generated.model,
                prompt_version=generated.prompt_version,
                retrieval_count=len(matches),
            )
        return RagResult(
            answer=generated.answer,
            sources=[source_by_id[item] for item in cited],
            support="grounded",
            provider=generated.provider,
            model=generated.model,
            prompt_version=generated.prompt_version,
            retrieval_count=len(matches),
        )

    def _unanswerable(self, *, retrieval_count: int) -> RagResult:
        return RagResult(
            answer=UNANSWERABLE,
            sources=[],
            support="unanswerable",
            provider=None,
            model=None,
            prompt_version=self.prompt_version,
            retrieval_count=retrieval_count,
        )


def _metadata_uuid(metadata: Mapping[str, object], key: str) -> uuid.UUID | None:
    value = metadata.get(key)
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None
