from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.dependencies import get_tenant_context
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.auth.service import AuthorizationService
from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.models import Document, DocumentPage, KnowledgeBase
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.ingestion.pdf import PdfValidationError
from dynamic_agentic_api.ingestion.service import INGESTION_VERSION
from dynamic_agentic_api.schemas import DocumentResponse, KnowledgeBaseCreate, KnowledgeBaseResponse
from dynamic_agentic_api.services import get_ai_services, get_core_services

router = APIRouter(prefix="/organizations/{organization_id}", tags=["knowledge"])
authorization = AuthorizationService()
_unsafe_filename = re.compile(r"[^A-Za-z0-9._ -]+")


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse, status_code=201)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> KnowledgeBaseResponse:
    authorization.require_permission(context, "knowledge_base.write")
    knowledge_base = KnowledgeBase(
        organization_id=context.organization_id,
        name=payload.name,
        status="active",
    )
    session.add(knowledge_base)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(
            status_code=409,
            code="KNOWLEDGE_BASE_EXISTS",
            message="A knowledge base with this name already exists.",
        ) from exc
    await session.refresh(knowledge_base)
    return KnowledgeBaseResponse.model_validate(knowledge_base)


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[KnowledgeBaseResponse]:
    authorization.require_permission(context, "knowledge_base.read")
    rows = await session.scalars(
        select(KnowledgeBase)
        .where(KnowledgeBase.organization_id == context.organization_id)
        .order_by(KnowledgeBase.name)
    )
    return [KnowledgeBaseResponse.model_validate(row) for row in rows]


@router.get("/knowledge-bases/{knowledge_base_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    knowledge_base_id: uuid.UUID,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[DocumentResponse]:
    authorization.require_permission(context, "knowledge_base.read")
    await _require_knowledge_base(session, context, knowledge_base_id)
    rows = await session.scalars(
        select(Document)
        .where(
            Document.organization_id == context.organization_id,
            Document.knowledge_base_id == knowledge_base_id,
        )
        .order_by(Document.created_at.desc())
    )
    return [DocumentResponse.model_validate(row) for row in rows]


@router.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    knowledge_base_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    file: Annotated[UploadFile, File()],
) -> DocumentResponse:
    authorization.require_permission(context, "knowledge_base.write")
    await _require_knowledge_base(session, context, knowledge_base_id)
    ai = get_ai_services()
    settings = get_settings()
    if file.content_type != "application/pdf":
        raise AppError(
            status_code=415,
            code="PDF_REQUIRED",
            message="Only PDF uploads are supported.",
        )
    if not file.filename or Path(file.filename).suffix.casefold() != ".pdf":
        raise AppError(
            status_code=415,
            code="PDF_EXTENSION_REQUIRED",
            message="The upload filename must use the .pdf extension.",
        )
    data = await file.read(settings.max_pdf_size_bytes + 1)
    if not data:
        raise AppError(status_code=422, code="EMPTY_UPLOAD", message="The uploaded PDF is empty.")
    if len(data) > settings.max_pdf_size_bytes:
        raise AppError(
            status_code=413,
            code="PDF_SIZE_LIMIT_EXCEEDED",
            message=f"The PDF exceeds the configured {settings.max_pdf_size_mb} MB limit.",
        )
    try:
        inspection = await get_core_services().pdf.inspect(data, settings.max_pdf_pages)
    except PdfValidationError as exc:
        raise AppError(
            status_code=422,
            code=str(exc),
            message="The uploaded PDF failed validation.",
        ) from exc
    checksum = hashlib.sha256(data).hexdigest()
    existing = await session.scalar(
        select(Document).where(
            Document.organization_id == context.organization_id,
            Document.knowledge_base_id == knowledge_base_id,
            Document.content_checksum == checksum,
        )
    )
    if existing:
        return DocumentResponse.model_validate(existing)
    document_id = uuid.uuid4()
    filename = _sanitize_filename(file.filename)
    source_ref = await get_core_services().storage.put(
        f"{context.organization_id}/documents/{document_id}/source.pdf", data
    )
    document = Document(
        id=document_id,
        organization_id=context.organization_id,
        knowledge_base_id=knowledge_base_id,
        filename=filename,
        content_checksum=checksum,
        mime_type="application/pdf",
        size_bytes=len(data),
        page_count=inspection.page_count,
        status="queued",
        source_object_ref=source_ref,
        ingestion_version=INGESTION_VERSION,
    )
    session.add(document)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        existing = await session.scalar(
            select(Document).where(
                Document.organization_id == context.organization_id,
                Document.knowledge_base_id == knowledge_base_id,
                Document.content_checksum == checksum,
            )
        )
        if existing:
            return DocumentResponse.model_validate(existing)
        raise AppError(
            status_code=409,
            code="DOCUMENT_UPLOAD_CONFLICT",
            message="The document could not be created because of a conflicting upload.",
        ) from exc
    background_tasks.add_task(ai.ingestion.run, document.id)
    return DocumentResponse.model_validate(document)


@router.post(
    "/documents/{document_id}/reindex",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reindex_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentResponse:
    authorization.require_permission(context, "knowledge_base.write")
    document = await session.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == context.organization_id,
        )
    )
    if document is None:
        raise AppError(status_code=404, code="DOCUMENT_NOT_FOUND", message="Document not found.")
    document.status = "queued"
    document.error_code = None
    await session.commit()
    background_tasks.add_task(get_ai_services().ingestion.run, document.id)
    return DocumentResponse.model_validate(document)


@router.get("/documents/{document_id}/pages/{page_number}/preview")
async def get_page_preview(
    document_id: uuid.UUID,
    page_number: int,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    authorization.require_permission(context, "knowledge_base.read")
    page = await session.scalar(
        select(DocumentPage)
        .join(
            Document,
            (Document.id == DocumentPage.document_id)
            & (Document.organization_id == DocumentPage.organization_id),
        )
        .where(
            DocumentPage.document_id == document_id,
            DocumentPage.organization_id == context.organization_id,
            DocumentPage.page_number == page_number,
            Document.organization_id == context.organization_id,
            Document.status == "ready",
        )
    )
    if page is None:
        raise AppError(
            status_code=404,
            code="SOURCE_PREVIEW_NOT_FOUND",
            message="The authorized source preview was not found.",
        )
    content = await get_core_services().storage.read(page.preview_object_ref)
    return Response(
        content=content,
        media_type="image/png",
        headers={"Cache-Control": "private, no-store", "Content-Disposition": "inline"},
    )


async def _require_knowledge_base(
    session: AsyncSession, context: TenantContext, knowledge_base_id: uuid.UUID
) -> KnowledgeBase:
    knowledge_base = await session.scalar(
        select(KnowledgeBase).where(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.organization_id == context.organization_id,
            KnowledgeBase.status == "active",
        )
    )
    if knowledge_base is None:
        raise AppError(
            status_code=404,
            code="KNOWLEDGE_BASE_NOT_FOUND",
            message="The knowledge base was not found.",
        )
    return knowledge_base


def _sanitize_filename(filename: str | None) -> str:
    basename = Path(filename or "document.pdf").name
    sanitized = _unsafe_filename.sub("_", basename).strip(" .")[:250]
    if not sanitized.casefold().endswith(".pdf"):
        sanitized = f"{sanitized or 'document'}.pdf"
    return sanitized
