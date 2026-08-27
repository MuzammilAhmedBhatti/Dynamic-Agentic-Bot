from __future__ import annotations

from dynamic_agentic_api.embeddings.providers import FakeEmbeddingProvider
from dynamic_agentic_api.ingestion.chunking import RecursivePageChunker
from dynamic_agentic_api.ingestion.contracts import ExtractedPage
from dynamic_agentic_api.vector_store.service import FakeVectorStore, VectorRecord


async def test_embedding_and_vector_abstractions_enforce_filters() -> None:
    embeddings = FakeEmbeddingProvider()
    first = await embeddings.embed_documents(["retention policy"])
    second = await embeddings.embed_query("retention policy")
    assert first.model == "fake-embedding-v1"
    assert first.dimension == len(first.vectors[0])
    assert first.vectors[0] == second.vectors[0]

    store = FakeVectorStore()
    await store.upsert(
        namespace="tenant-a",
        records=[
            VectorRecord(
                id="allowed",
                values=first.vectors[0],
                metadata={"tenant_id": "tenant-a", "knowledge_base_id": "kb-a"},
            ),
            VectorRecord(
                id="other-kb",
                values=first.vectors[0],
                metadata={"tenant_id": "tenant-a", "knowledge_base_id": "kb-b"},
            ),
        ],
    )
    matches = await store.query(
        namespace="tenant-a",
        vector=second.vectors[0],
        top_k=5,
        filters={"tenant_id": "tenant-a", "knowledge_base_id": "kb-a"},
    )
    assert [match.id for match in matches] == ["allowed"]
    assert (
        await store.query(
            namespace="tenant-b",
            vector=second.vectors[0],
            top_k=5,
            filters={"tenant_id": "tenant-b", "knowledge_base_id": "kb-a"},
        )
        == []
    )
    await store.delete_document(namespace="tenant-a", document_id="missing")
    assert [
        match.id
        for match in await store.query(
            namespace="tenant-a",
            vector=second.vectors[0],
            top_k=5,
            filters={"tenant_id": "tenant-a", "knowledge_base_id": "kb-a"},
        )
    ] == ["allowed"]


def test_chunk_boundaries_preserve_page_metadata() -> None:
    chunker = RecursivePageChunker(chunk_size=80, overlap=10)
    pages = [
        ExtractedPage(
            page_number=7,
            text="First paragraph about retention.\n\n" + "Second paragraph. " * 8,
            preview_png=b"png",
            title="Retention",
            section="Policy",
        )
    ]
    chunks = chunker.chunk_pages(pages)
    assert len(chunks) > 1
    assert all(chunk.page_number == 7 for chunk in chunks)
    assert all(
        chunk.title == "Retention" and chunk.section == "Policy" for chunk in chunks
    )
    assert all(len(chunk.text) <= 90 for chunk in chunks)
