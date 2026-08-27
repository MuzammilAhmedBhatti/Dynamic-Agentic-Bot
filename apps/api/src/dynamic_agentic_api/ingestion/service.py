from __future__ import annotations

import hashlib
import uuid

from sqlalchemy import delete, select

from dynamic_agentic_api.config import Settings
from dynamic_agentic_api.db.models import Document, DocumentChunk, DocumentPage
from dynamic_agentic_api.db.session import async_session_factory
from dynamic_agentic_api.embeddings.providers import EmbeddingProvider
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.ingestion.chunking import RecursivePageChunker
from dynamic_agentic_api.ingestion.ocr import OcrService
from dynamic_agentic_api.ingestion.pdf import PdfProcessor, PdfValidationError
from dynamic_agentic_api.ingestion.scanning import MalwareScanner
from dynamic_agentic_api.observability import get_logger
from dynamic_agentic_api.storage.service import StorageService
from dynamic_agentic_api.vector_store.service import VectorMetadata, VectorRecord, VectorStore

logger = get_logger()
INGESTION_VERSION = "pdf-rag-v1"


class IngestionService:
    def __init__(
        self,
        *,
        settings: Settings,
        storage: StorageService,
        scanner: MalwareScanner,
        pdf: PdfProcessor,
        ocr: OcrService,
        embeddings: EmbeddingProvider,
        vectors: VectorStore,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._scanner = scanner
        self._pdf = pdf
        self._ocr = ocr
        self._embeddings = embeddings
        self._vectors = vectors
        self._chunker = RecursivePageChunker(
            chunk_size=settings.chunk_size_chars,
            overlap=settings.chunk_overlap_chars,
        )

    async def run(self, document_id: uuid.UUID) -> None:
        try:
            await self._run(document_id)
        except AppError as exc:
            await self._mark_failed(document_id, exc.code)
        except PdfValidationError as exc:
            await self._mark_failed(document_id, str(exc))
        except Exception as exc:
            logger.exception(
                "document_ingestion_failed",
                document_id=str(document_id),
                error_type=type(exc).__name__,
            )
            await self._mark_failed(document_id, "INGESTION_FAILED")

    async def _run(self, document_id: uuid.UUID) -> None:
        async with async_session_factory() as session:
            document = await session.get(Document, document_id)
            if document is None:
                return
            document.status = "processing"
            document.error_code = None
            await session.commit()
            source_ref = document.source_object_ref
            filename = document.filename
            organization_id = document.organization_id
            knowledge_base_id = document.knowledge_base_id

        source = await self._storage.read(source_ref)
        scan = await self._scanner.scan(source, filename)
        if not scan.clean:
            raise AppError(
                status_code=422,
                code=scan.reason_code or "MALWARE_SCAN_FAILED",
                message="The document failed security validation.",
            )
        pages = await self._pdf.extract_and_render(source, self._settings.max_pdf_pages)
        hydrated_pages = []
        for page in pages:
            if len(page.text.strip()) < 10:
                ocr_text = await self._ocr.extract_page_text(page.preview_png)
                if ocr_text:
                    page = type(page)(
                        page_number=page.page_number,
                        text=ocr_text.strip(),
                        preview_png=page.preview_png,
                        title=page.title,
                        section=page.section,
                    )
            hydrated_pages.append(page)
        if not any(len(page.text.strip()) >= 10 for page in hydrated_pages):
            async with async_session_factory() as session:
                document = await session.get(Document, document_id)
                if document:
                    document.status = "ocr_required"
                    document.error_code = "OCR_REQUIRED"
                    document.page_count = len(hydrated_pages)
                    await session.commit()
            return

        chunks = self._chunker.chunk_pages(hydrated_pages)
        if not chunks:
            raise AppError(
                status_code=422,
                code="NO_USABLE_TEXT",
                message="No usable text was extracted from the document.",
            )

        # Re-indexing is replacement, not additive: remove prior vectors before
        # deterministic chunk IDs are regenerated so stale chunks cannot survive.
        await self._vectors.delete_document(
            namespace=str(organization_id), document_id=str(document_id)
        )

        async with async_session_factory() as session:
            await session.execute(
                delete(DocumentPage).where(DocumentPage.document_id == document_id)
            )
            page_rows: dict[int, DocumentPage] = {}
            for page in hydrated_pages:
                prefix = f"{organization_id}/documents/{document_id}/pages/{page.page_number}"
                text_bytes = page.text.encode("utf-8")
                text_ref = await self._storage.put(f"{prefix}/text.txt", text_bytes)
                preview_ref = await self._storage.put(f"{prefix}/preview.png", page.preview_png)
                page_row = DocumentPage(
                    organization_id=organization_id,
                    document_id=document_id,
                    page_number=page.page_number,
                    text_object_ref=text_ref,
                    preview_object_ref=preview_ref,
                    text_checksum=hashlib.sha256(text_bytes).hexdigest(),
                    extracted_character_count=len(page.text),
                )
                session.add(page_row)
                page_rows[page.page_number] = page_row
            await session.flush()
            chunk_rows: list[DocumentChunk] = []
            for chunk in chunks:
                chunk_id = uuid.uuid4()
                chunk_bytes = chunk.text.encode("utf-8")
                chunk_ref = await self._storage.put(
                    f"{organization_id}/documents/{document_id}/chunks/{chunk_id}.txt",
                    chunk_bytes,
                )
                vector_id = str(
                    uuid.uuid5(
                        document_id, f"{chunk.ordinal}:{hashlib.sha256(chunk_bytes).hexdigest()}"
                    )
                )
                chunk_row = DocumentChunk(
                    id=chunk_id,
                    organization_id=organization_id,
                    knowledge_base_id=knowledge_base_id,
                    document_id=document_id,
                    page_id=page_rows[chunk.page_number].id,
                    page_number=chunk.page_number,
                    ordinal=chunk.ordinal,
                    text_object_ref=chunk_ref,
                    content_checksum=hashlib.sha256(chunk_bytes).hexdigest(),
                    section=chunk.section,
                    title=chunk.title,
                    chunker_version=chunk.chunker_version,
                    chunk_size=chunk.chunk_size,
                    chunk_overlap=chunk.overlap,
                    vector_id=vector_id,
                )
                session.add(chunk_row)
                chunk_rows.append(chunk_row)
            document = await session.get(Document, document_id)
            if document:
                document.page_count = len(hydrated_pages)
            await session.commit()

        vectors: list[list[float]] = []
        model = ""
        dimension = 0
        for start in range(0, len(chunks), 100):
            batch = await self._embeddings.embed_documents(
                [chunk.text for chunk in chunks[start : start + 100]]
            )
            if model and (batch.model != model or batch.dimension != dimension):
                raise AppError(
                    status_code=503,
                    code="INCOMPATIBLE_EMBEDDING_BATCH",
                    message=(
                        "The embedding model changed during ingestion; re-indexing is required."
                    ),
                )
            model, dimension = batch.model, batch.dimension
            vectors.extend(batch.vectors)
        records = []
        for chunk_row, vector in zip(chunk_rows, vectors, strict=True):
            metadata: VectorMetadata = {
                "tenant_id": str(organization_id),
                "knowledge_base_id": str(knowledge_base_id),
                "document_id": str(document_id),
                "chunk_id": str(chunk_row.id),
                "filename": filename,
                "page_number": chunk_row.page_number,
                "title": chunk_row.title or "",
                "section": chunk_row.section or "",
                "embedding_model": model,
                "embedding_version": model,
                "ingestion_version": INGESTION_VERSION,
                "chunker_version": chunk_row.chunker_version,
                "text_ref": chunk_row.text_object_ref,
                "preview_ref": page_rows[chunk_row.page_number].preview_object_ref,
                "content_checksum": chunk_row.content_checksum,
            }
            records.append(VectorRecord(id=chunk_row.vector_id, values=vector, metadata=metadata))
        await self._vectors.upsert(namespace=str(organization_id), records=records)

        async with async_session_factory() as session:
            document = await session.get(Document, document_id)
            if document:
                document.status = "ready"
                document.error_code = None
                document.embedding_model = model
                document.embedding_dimension = dimension
                await session.commit()
        logger.info(
            "document_ingestion_completed",
            document_id=str(document_id),
            page_count=len(hydrated_pages),
            chunk_count=len(chunks),
            embedding_model=model,
        )

    @staticmethod
    async def _mark_failed(document_id: uuid.UUID, code: str) -> None:
        async with async_session_factory() as session:
            document = await session.scalar(select(Document).where(Document.id == document_id))
            if document:
                document.status = "failed"
                document.error_code = code[:100]
                await session.commit()
