from __future__ import annotations

import asyncio
import hashlib
import math
from dataclasses import dataclass
from typing import Protocol

from google import genai
from google.genai import types

from dynamic_agentic_api.errors import AppError


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    vectors: list[list[float]]
    model: str
    dimension: int


class EmbeddingProvider(Protocol):
    async def embed_documents(self, texts: list[str]) -> EmbeddingResult: ...

    async def embed_query(self, text: str) -> EmbeddingResult: ...


class VertexEmbeddingProvider:
    provider_name = "vertex-ai"

    def __init__(
        self,
        *,
        project: str,
        location: str,
        model: str,
        dimension: int,
        timeout_seconds: float,
        max_attempts: int,
    ) -> None:
        self.model = model
        self.dimension = dimension
        self._timeout = timeout_seconds
        self._max_attempts = max_attempts
        self._client = genai.Client(vertexai=True, project=project, location=location)

    async def embed_documents(self, texts: list[str]) -> EmbeddingResult:
        return await self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

    async def embed_query(self, text: str) -> EmbeddingResult:
        return await self._embed([text], task_type="RETRIEVAL_QUERY")

    async def _embed(self, texts: list[str], *, task_type: str) -> EmbeddingResult:
        if not texts:
            return EmbeddingResult(vectors=[], model=self.model, dimension=self.dimension)
        last_error: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                async with asyncio.timeout(self._timeout):
                    response = await self._client.aio.models.embed_content(
                        model=self.model,
                        contents=texts,
                        config=types.EmbedContentConfig(
                            task_type=task_type,
                            output_dimensionality=self.dimension,
                            auto_truncate=True,
                        ),
                    )
                vectors = [list(item.values or []) for item in (response.embeddings or [])]
                if len(vectors) != len(texts) or any(
                    len(vector) != self.dimension for vector in vectors
                ):
                    raise ValueError("embedding response shape mismatch")
                return EmbeddingResult(vectors=vectors, model=self.model, dimension=self.dimension)
            except Exception as exc:  # SDK error types vary by transport.
                last_error = exc
                if attempt + 1 < self._max_attempts:
                    await asyncio.sleep(min(0.25 * (2**attempt), 2.0))
        raise AppError(
            status_code=503,
            code="EMBEDDING_PROVIDER_UNAVAILABLE",
            message="The embedding service is temporarily unavailable.",
            retryable=True,
        ) from last_error


class FakeEmbeddingProvider:
    """Deterministic test-only provider selected only when APP_ENV=test."""

    model = "fake-embedding-v1"
    dimension = 16

    async def embed_documents(self, texts: list[str]) -> EmbeddingResult:
        return EmbeddingResult(
            vectors=[self._vector(text) for text in texts],
            model=self.model,
            dimension=self.dimension,
        )

    async def embed_query(self, text: str) -> EmbeddingResult:
        return await self.embed_documents([text])

    def _vector(self, text: str) -> list[float]:
        values = [0.0] * self.dimension
        for token in text.casefold().split():
            digest = hashlib.sha256(token.encode()).digest()
            values[digest[0] % self.dimension] += 1.0 if digest[1] % 2 else -1.0
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]
