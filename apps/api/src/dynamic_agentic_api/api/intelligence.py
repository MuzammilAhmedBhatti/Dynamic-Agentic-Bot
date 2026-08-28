from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.dependencies import authorization_service, get_tenant_context
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.data_sources.security import SqlGuard
from dynamic_agentic_api.db.models import DataSource, KnowledgeBase
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.schemas import (
    DataSourceCreate,
    DataSourceResponse,
    PersonaResponse,
    ProviderModelResponse,
)
from dynamic_agentic_api.services import get_ai_services

router = APIRouter(prefix="/organizations/{organization_id}", tags=["intelligence"])


@router.get("/personas", response_model=list[PersonaResponse])
async def list_personas(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
) -> list[PersonaResponse]:
    authorization_service.require_permission(context, "chat.execute")
    return [
        PersonaResponse(
            id=item.id,
            slug=item.slug,
            name=item.name,
            description=item.description,
            allowed_routes=list(item.allowed_routes),
            default_provider=item.default_provider,
            default_model=item.default_model,
            scope=item.scope,
            is_active=item.is_active,
        )
        for item in get_ai_services().personas.list_active()
    ]


@router.get("/provider-models", response_model=list[ProviderModelResponse])
async def list_provider_models(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
) -> list[ProviderModelResponse]:
    authorization_service.require_permission(context, "chat.execute")
    return [
        ProviderModelResponse(
            provider=item.provider,
            model=item.model,
            available=item.available,
            reason=item.reason,
        )
        for item in get_ai_services().llms.list_models()
    ]


@router.get("/data-sources", response_model=list[DataSourceResponse])
async def list_data_sources(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    knowledge_base_id: uuid.UUID | None = None,
) -> list[DataSourceResponse]:
    authorization_service.require_permission(context, "knowledge_base.read")
    statement = select(DataSource).where(DataSource.organization_id == context.organization_id)
    if knowledge_base_id:
        statement = statement.where(DataSource.knowledge_base_id == knowledge_base_id)
    rows = (await session.scalars(statement.order_by(DataSource.name))).all()
    return [_response(item) for item in rows]


@router.post("/data-sources", response_model=DataSourceResponse, status_code=201)
async def create_data_source(
    payload: DataSourceCreate,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DataSourceResponse:
    authorization_service.require_permission(context, "knowledge_base.write")
    knowledge_base = await session.scalar(
        select(KnowledgeBase.id).where(
            KnowledgeBase.id == payload.knowledge_base_id,
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
    SqlGuard.validate_identifier(payload.allowed_schema)
    tables = list(dict.fromkeys(payload.allowed_tables))
    for table in tables:
        SqlGuard.validate_identifier(table)
    ai = get_ai_services()
    connection_url = ai.database.validate_connection_url(payload.connection_url)
    source = DataSource(
        organization_id=context.organization_id,
        knowledge_base_id=payload.knowledge_base_id,
        name=" ".join(payload.name.split()),
        kind=payload.kind,
        encrypted_connection=ai.cipher.encrypt(connection_url),
        allowed_schema=payload.allowed_schema,
        allowed_tables=tables,
    )
    session.add(source)
    await session.flush()
    await ai.database.discover_schema(source)
    await session.commit()
    return _response(source)


def _response(source: DataSource) -> DataSourceResponse:
    return DataSourceResponse(
        id=source.id,
        organization_id=source.organization_id,
        knowledge_base_id=source.knowledge_base_id,
        name=source.name,
        kind=source.kind,
        allowed_schema=source.allowed_schema,
        allowed_tables=source.allowed_tables,
        is_active=source.is_active,
    )
