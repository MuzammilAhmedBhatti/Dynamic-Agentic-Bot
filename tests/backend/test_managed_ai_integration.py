from __future__ import annotations

import os

import pytest
from dynamic_agentic_api.embeddings.providers import VertexEmbeddingProvider
from dynamic_agentic_api.llm.gateway import (
    EvidenceBlock,
    LlmRequest,
    VertexGeminiProvider,
)
from dynamic_agentic_api.vector_store.service import PineconeVectorStore


@pytest.mark.managed_integration
async def test_real_vertex_and_pinecone_path_when_explicitly_enabled() -> None:
    if os.getenv("RUN_MANAGED_AI_INTEGRATION") != "1":
        pytest.skip(
            "set RUN_MANAGED_AI_INTEGRATION=1 with ADC and Pinecone credentials"
        )
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    embedding_model = os.getenv("VERTEX_EMBEDDING_MODEL", "gemini-embedding-001")
    dimension = int(os.getenv("VERTEX_EMBEDDING_DIMENSION", "768"))
    embeddings = VertexEmbeddingProvider(
        project=project,
        location=location,
        model=embedding_model,
        dimension=dimension,
        timeout_seconds=30,
        max_attempts=2,
    )
    embedded = await embeddings.embed_query("managed integration health check")
    assert len(embedded.vectors[0]) == dimension
    vectors = PineconeVectorStore(
        api_key=os.environ["PINECONE_API_KEY"],
        index_name=os.environ["PINECONE_INDEX"],
        index_host=os.getenv("PINECONE_INDEX_HOST"),
        timeout_seconds=30,
    )
    assert (
        await vectors.query(
            namespace="integration-health-check",
            vector=embedded.vectors[0],
            top_k=1,
            filters={"tenant_id": "integration-health-check"},
        )
        == []
    )
    llm = VertexGeminiProvider(
        project=project,
        location=location,
        model=os.getenv("VERTEX_GEMINI_MODEL", "gemini-2.5-flash"),
        timeout_seconds=30,
        max_attempts=2,
    )
    result = await llm.generate_grounded_answer(
        LlmRequest(
            question="What color is the test token?",
            evidence=[
                EvidenceBlock("chunk-1", "fixture", 1, "The test token is blue.")
            ],
            prompt_version="integration-v1",
        )
    )
    assert "chunk-1" in result.cited_chunk_ids
