from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import Any, Protocol, cast

from pinecone import Pinecone

from dynamic_agentic_api.errors import AppError

MetadataValue = str | int | float | bool | list[str]
VectorMetadata = dict[str, MetadataValue]


@dataclass(frozen=True, slots=True)
class VectorRecord:
    id: str
    values: list[float]
    metadata: VectorMetadata


@dataclass(frozen=True, slots=True)
class VectorMatch:
    id: str
    score: float
    metadata: VectorMetadata


class VectorStore(Protocol):
    async def upsert(self, *, namespace: str, records: list[VectorRecord]) -> None: ...

    async def query(
        self,
        *,
        namespace: str,
        vector: list[float],
        top_k: int,
        filters: VectorMetadata,
    ) -> list[VectorMatch]: ...

    async def delete_document(self, *, namespace: str, document_id: str) -> None: ...


class PineconeVectorStore:
    def __init__(
        self,
        *,
        api_key: str,
        index_name: str,
        index_host: str | None,
        timeout_seconds: float,
    ) -> None:
        client = Pinecone(api_key=api_key)
        self._index = client.Index(host=index_host) if index_host else client.Index(index_name)
        self._timeout = timeout_seconds
        self._validated_dimension: int | None = None

    async def upsert(self, *, namespace: str, records: list[VectorRecord]) -> None:
        if not records:
            return
        dimension = len(records[0].values)
        if any(len(record.values) != dimension for record in records):
            raise ValueError("vector batch contains incompatible dimensions")
        if self._validated_dimension != dimension:
            try:
                stats = await asyncio.to_thread(self._index.describe_index_stats)
            except Exception as exc:
                raise _unavailable("VECTOR_INDEX_UNAVAILABLE") from exc
            if int(stats.dimension) != dimension:
                raise AppError(
                    status_code=503,
                    code="PINECONE_DIMENSION_MISMATCH",
                    message=(
                        "The Pinecone index dimension does not match the embedding model; "
                        "re-indexing is required."
                    ),
                )
            self._validated_dimension = dimension
        payload: list[dict[str, Any]] = [
            {"id": record.id, "values": record.values, "metadata": record.metadata}
            for record in records
        ]
        try:
            await asyncio.to_thread(
                self._index.upsert,
                vectors=cast(Any, payload),
                namespace=namespace,
                batch_size=100,
                show_progress=False,
                timeout=self._timeout,
            )
        except Exception as exc:
            raise _unavailable("VECTOR_INDEX_UNAVAILABLE") from exc

    async def query(
        self,
        *,
        namespace: str,
        vector: list[float],
        top_k: int,
        filters: VectorMetadata,
    ) -> list[VectorMatch]:
        pinecone_filter: Any = {key: {"$eq": value} for key, value in filters.items()}
        try:
            response = cast(
                Any,
                await asyncio.to_thread(
                    self._index.query,
                    vector=vector,
                    top_k=top_k,
                    namespace=namespace,
                    filter=pinecone_filter,
                    include_metadata=True,
                    include_values=False,
                    timeout=self._timeout,
                ),
            )
        except Exception as exc:
            raise _unavailable("VECTOR_RETRIEVAL_UNAVAILABLE") from exc
        matches: list[VectorMatch] = []
        for match in response.matches:
            metadata = _safe_metadata(dict(match.metadata or {}))
            matches.append(
                VectorMatch(id=str(match.id), score=float(match.score), metadata=metadata)
            )
        return matches

    async def delete_document(self, *, namespace: str, document_id: str) -> None:
        try:
            await asyncio.to_thread(
                self._index.delete,
                namespace=namespace,
                filter=cast(Any, {"document_id": {"$eq": document_id}}),
                timeout=self._timeout,
            )
        except Exception as exc:
            raise _unavailable("VECTOR_DELETE_UNAVAILABLE") from exc


class FakeVectorStore:
    """In-memory test-only implementation with the same tenant/filter semantics."""

    def __init__(self) -> None:
        self.records: dict[str, dict[str, VectorRecord]] = {}

    async def upsert(self, *, namespace: str, records: list[VectorRecord]) -> None:
        bucket = self.records.setdefault(namespace, {})
        for record in records:
            bucket[record.id] = record

    async def query(
        self,
        *,
        namespace: str,
        vector: list[float],
        top_k: int,
        filters: VectorMetadata,
    ) -> list[VectorMatch]:
        candidates = []
        for record in self.records.get(namespace, {}).values():
            if all(record.metadata.get(key) == value for key, value in filters.items()):
                candidates.append(
                    VectorMatch(
                        id=record.id,
                        score=_cosine(vector, record.values),
                        metadata=record.metadata,
                    )
                )
        return sorted(candidates, key=lambda item: item.score, reverse=True)[:top_k]

    async def delete_document(self, *, namespace: str, document_id: str) -> None:
        bucket = self.records.get(namespace, {})
        for record_id in [
            key for key, value in bucket.items() if value.metadata.get("document_id") == document_id
        ]:
            del bucket[record_id]

    def clear(self) -> None:
        self.records.clear()


def _safe_metadata(raw: dict[str, object]) -> VectorMetadata:
    safe: VectorMetadata = {}
    for key, value in raw.items():
        if isinstance(value, (str, int, float, bool)):
            safe[key] = value
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            safe[key] = value
    return safe


def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return -1.0
    denominator = math.sqrt(sum(v * v for v in left)) * math.sqrt(sum(v * v for v in right))
    return (
        sum(a * b for a, b in zip(left, right, strict=True)) / denominator if denominator else 0.0
    )


def _unavailable(code: str) -> AppError:
    return AppError(
        status_code=503,
        code=code,
        message="The vector service is temporarily unavailable.",
        retryable=True,
    )
