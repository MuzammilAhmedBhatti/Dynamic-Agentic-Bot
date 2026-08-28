from __future__ import annotations

import asyncio
import uuid
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.agents.document_graph import GRAPH_VERSION
from dynamic_agentic_api.auth.dependencies import (
    authorization_service,
    get_tenant_context,
    identity_provider,
)
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.models import AgentRun, AgentTraceEvent, DataSource, KnowledgeBase
from dynamic_agentic_api.db.session import async_session_factory, get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.schemas import (
    CalculationResponse,
    ChatRunCreate,
    ChatRunCreated,
    ChatRunExecute,
    ChatRunResponse,
    CitationSourceResponse,
    DatabaseEvidenceResponse,
    PersonaResponse,
)
from dynamic_agentic_api.services import get_ai_services, get_core_services

router = APIRouter(prefix="/organizations/{organization_id}/chat/runs", tags=["chat"])


@router.post("", response_model=ChatRunCreated, status_code=201)
async def create_chat_run(
    payload: ChatRunCreate,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatRunCreated:
    authorization_service.require_permission(context, "chat.execute")
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
    ai = get_ai_services()
    if payload.persona_id is not None:
        ai.personas.get_by_id(payload.persona_id)
    selected_llm = ai.llms.resolve(payload.provider, payload.model)
    if payload.data_source_id is not None:
        source = await session.scalar(
            select(DataSource.id).where(
                DataSource.id == payload.data_source_id,
                DataSource.organization_id == context.organization_id,
                DataSource.knowledge_base_id == payload.knowledge_base_id,
                DataSource.is_active.is_(True),
            )
        )
        if source is None:
            raise AppError(
                status_code=404,
                code="DATA_SOURCE_NOT_FOUND",
                message="The data source was not found.",
            )
    run = AgentRun(
        organization_id=context.organization_id,
        user_id=context.user_id,
        knowledge_base_id=payload.knowledge_base_id,
        trace_id=str(uuid.uuid4()),
        status="queued",
        graph_version=GRAPH_VERSION,
        prompt_version="grounded-rag-v1",
        persona_id=payload.persona_id,
        data_source_id=payload.data_source_id,
        provider=selected_llm.provider_name,
        model=selected_llm.model,
    )
    session.add(run)
    await session.commit()
    return ChatRunCreated(run_id=run.id, trace_id=run.trace_id, status=run.status)


@router.post("/{run_id}/execute", response_model=ChatRunResponse)
async def execute_chat_run(
    run_id: uuid.UUID,
    payload: ChatRunExecute,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatRunResponse:
    authorization_service.require_permission(context, "chat.execute")
    run = await session.scalar(
        select(AgentRun).where(
            AgentRun.id == run_id,
            AgentRun.organization_id == context.organization_id,
            AgentRun.user_id == context.user_id,
        )
    )
    if run is None:
        raise AppError(
            status_code=404, code="CHAT_RUN_NOT_FOUND", message="The chat run was not found."
        )
    if run.status != "queued":
        raise AppError(
            status_code=409,
            code="CHAT_RUN_NOT_EXECUTABLE",
            message="The chat run has already been executed.",
        )
    ai = get_ai_services()
    run.status = "running"
    await session.commit()
    try:
        result = await ai.graph.run(
            session=session,
            context=context,
            run_id=run.id,
            trace_id=run.trace_id,
            knowledge_base_id=run.knowledge_base_id,
            question=payload.question,
            persona_id=run.persona_id,
            data_source_id=run.data_source_id,
            provider=run.provider,
            model=run.model,
        )
    except Exception as exc:
        run.status = "failed"
        run.error_code = exc.code if isinstance(exc, AppError) else "WORKFLOW_FAILED"
        await session.commit()
        raise
    run.status = "completed"
    run.persona_id = result.persona.id
    run.provider = result.provider
    run.model = result.model
    run.route = "+".join(result.routes)
    await session.commit()
    return ChatRunResponse(
        run_id=run.id,
        trace_id=run.trace_id,
        answer=result.answer,
        support=result.support,  # type: ignore[arg-type]
        persona=PersonaResponse(
            id=result.persona.id,
            slug=result.persona.slug,
            name=result.persona.name,
            description=result.persona.description,
            allowed_routes=list(result.persona.allowed_routes),
            default_provider=result.persona.default_provider,
            default_model=result.persona.default_model,
            scope=result.persona.scope,
            is_active=result.persona.is_active,
        ),
        route=result.routes,
        sources=[
            CitationSourceResponse.model_validate(asdict(source))
            for source in (result.rag.sources if result.rag else [])
        ],
        provider=result.provider,
        model=result.model,
        graph_version=run.graph_version,
        prompt_version=result.prompt_version,
        calculations=[
            CalculationResponse.model_validate(asdict(item)) for item in result.calculations
        ],
        database_evidence=(
            [
                DatabaseEvidenceResponse(
                    source_id=result.database.source_id,
                    database_name=result.database.database_name,
                    tables=result.database.tables,
                    columns=result.database.columns,
                    row_count=result.database.row_count,
                )
            ]
            if result.database
            else []
        ),
        suggestions=result.suggestions,
    )


@router.websocket("/{run_id}/trace")
async def trace_chat_run(
    websocket: WebSocket, organization_id: uuid.UUID, run_id: uuid.UUID
) -> None:
    settings = get_settings()
    origin = websocket.headers.get("origin")
    if origin and origin not in settings.cors_origin_list:
        await websocket.close(code=4403, reason="Origin denied")
        return
    try:
        user = await identity_provider.authenticate(websocket)
        async with async_session_factory() as session:
            context = await authorization_service.resolve_tenant_context(
                session, user, organization_id
            )
            authorization_service.require_permission(context, "chat.execute")
            run = await session.scalar(
                select(AgentRun).where(
                    AgentRun.id == run_id,
                    AgentRun.organization_id == context.organization_id,
                    AgentRun.user_id == context.user_id,
                )
            )
            if run is None:
                raise AppError(
                    status_code=404,
                    code="CHAT_RUN_NOT_FOUND",
                    message="The chat run was not found.",
                )
    except AppError as exc:
        await websocket.close(code=4401 if exc.status_code == 401 else 4403, reason="Unauthorized")
        return

    hub = get_core_services().traces.hub
    try:
        async with hub.subscribe(run_id) as queue:
            # Complete the handshake only after the subscriber is registered.
            # The frontend executes the run immediately after onopen, so the
            # reverse order could lose every fast live event.
            await websocket.accept()
            async with async_session_factory() as session:
                replay = (
                    await session.scalars(
                        select(AgentTraceEvent)
                        .where(AgentTraceEvent.run_id == run_id)
                        .order_by(AgentTraceEvent.sequence)
                    )
                ).all()
                current_run = await session.get(AgentRun, run_id)
            last_sequence = 0
            for stored_event in replay:
                last_sequence = stored_event.sequence
                await websocket.send_json(_stored_event_payload(stored_event))
            if current_run and current_run.status in {"completed", "failed"}:
                await websocket.close(code=1000)
                return
            while True:
                try:
                    trace_event = await asyncio.wait_for(queue.get(), timeout=15)
                except TimeoutError:
                    await websocket.send_json({"event_type": "heartbeat", "run_id": str(run_id)})
                    continue
                if trace_event.sequence <= last_sequence:
                    continue
                last_sequence = trace_event.sequence
                await websocket.send_json(trace_event.to_dict())
                if trace_event.event_type in {"response_completed", "error"}:
                    await websocket.close(code=1000)
                    return
    except WebSocketDisconnect:
        return


def _stored_event_payload(event: AgentTraceEvent) -> dict[str, object]:
    return {
        "sequence": event.sequence,
        "run_id": str(event.run_id),
        "event_type": event.event_type,
        "stage": event.stage,
        "occurred_at": event.occurred_at.isoformat(),
        "duration_ms": event.duration_ms,
        "safe_summary": event.safe_summary,
    }
