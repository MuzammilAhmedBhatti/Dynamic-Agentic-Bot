from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.rag.service import RagResult, RagService
from dynamic_agentic_api.tracing.service import TraceService

GRAPH_VERSION = "document-rag-graph-v1"


class AgentState(TypedDict):
    run_id: uuid.UUID
    trace_id: str
    question: str
    knowledge_base_id: uuid.UUID
    persona: NotRequired[str]
    route: NotRequired[str]
    rag_result: NotRequired[RagResult]
    answer: NotRequired[str]
    support: NotRequired[str]


@dataclass(frozen=True, slots=True)
class GraphResult:
    answer: str
    rag: RagResult


class DocumentRagGraph:
    def __init__(self, *, rag: RagService, traces: TraceService) -> None:
        self._rag = rag
        self._traces = traces

    async def run(
        self,
        *,
        session: AsyncSession,
        context: TenantContext,
        run_id: uuid.UUID,
        trace_id: str,
        knowledge_base_id: uuid.UUID,
        question: str,
    ) -> GraphResult:
        async def emit(
            event_type: str, stage: str, summary: dict[str, object] | None = None
        ) -> None:
            await self._traces.emit(
                run_id=run_id,
                event_type=event_type,
                stage=stage,
                safe_summary=summary,
            )

        async def guard(state: AgentState) -> dict[str, object]:
            started = time.perf_counter()
            normalized = state["question"].strip()
            if not normalized or len(normalized) > 4000:
                raise AppError(
                    status_code=422,
                    code="INVALID_QUESTION",
                    message="The question must contain between 1 and 4000 characters.",
                )
            await self._traces.emit(
                run_id=run_id,
                event_type="request_received",
                stage="security_input_guard",
                duration_ms=round((time.perf_counter() - started) * 1000),
            )
            await emit("authorization_passed", "authorization")
            return {"question": normalized}

        async def persona_context(state: AgentState) -> dict[str, object]:
            del state
            return {"persona": "General Assistant"}

        async def router(state: AgentState) -> dict[str, object]:
            del state
            await emit("router_completed", "intent_router", {"route": "document_rag"})
            return {"route": "document_rag"}

        async def document_rag(state: AgentState) -> dict[str, object]:
            result = await self._rag.answer(
                session=session,
                context=context,
                knowledge_base_id=state["knowledge_base_id"],
                question=state["question"],
                trace=emit,
            )
            return {"rag_result": result}

        async def validate_grounding(state: AgentState) -> dict[str, object]:
            result = state["rag_result"]
            await emit(
                "citation_validation_completed",
                "grounding_citation_validation",
                {"citation_count": len(result.sources), "support": result.support},
            )
            return {"support": result.support}

        async def formatter(state: AgentState) -> dict[str, object]:
            result = state["rag_result"]
            return {"answer": result.answer}

        builder = StateGraph(AgentState)
        builder.add_node("security_input_guard", guard)
        builder.add_node("persona_context", persona_context)
        builder.add_node("router", router)
        builder.add_node("document_rag", document_rag)
        builder.add_node("grounding_citation_validation", validate_grounding)
        builder.add_node("formatter", formatter)
        builder.add_edge(START, "security_input_guard")
        builder.add_edge("security_input_guard", "persona_context")
        builder.add_edge("persona_context", "router")
        builder.add_edge("router", "document_rag")
        builder.add_edge("document_rag", "grounding_citation_validation")
        builder.add_edge("grounding_citation_validation", "formatter")
        builder.add_edge("formatter", END)
        graph = builder.compile()
        try:
            final = await graph.ainvoke(
                AgentState(
                    run_id=run_id,
                    trace_id=trace_id,
                    question=question,
                    knowledge_base_id=knowledge_base_id,
                )
            )
        except Exception as exc:
            await emit(
                "error",
                "workflow",
                {"error_code": exc.code if isinstance(exc, AppError) else "WORKFLOW_FAILED"},
            )
            raise
        result = final["rag_result"]
        await emit(
            "response_completed",
            "formatter",
            {"support": result.support, "citation_count": len(result.sources)},
        )
        return GraphResult(answer=final["answer"], rag=result)
