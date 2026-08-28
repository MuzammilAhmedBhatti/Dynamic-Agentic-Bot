from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.data_sources.service import DatabaseQueryResult, PostgresConnector
from dynamic_agentic_api.db.models import DataSource
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.llm.gateway import AgentPlan, LlmProvider, SqlGenerationRequest
from dynamic_agentic_api.llm.registry import LlmRegistry
from dynamic_agentic_api.math.service import CalculationRequest, CalculationResult, MathService
from dynamic_agentic_api.personas.service import PersonaDefinition, PersonaRegistry
from dynamic_agentic_api.rag.service import UNANSWERABLE, RagResult, RagService
from dynamic_agentic_api.tracing.service import TraceService

GRAPH_VERSION = "dynamic-agent-graph-v2"
_EXPLICIT_DATABASE_MARKERS = (
    "database",
    "data source",
    "sql",
    "table",
    "customers",
    "orders",
    "sales",
)


def normalize_plan_for_selected_sources(
    plan: AgentPlan, *, question: str, has_data_source: bool
) -> AgentPlan:
    routes = list(plan.routes)
    lowered = question.casefold()
    explicitly_requests_database = any(marker in lowered for marker in _EXPLICIT_DATABASE_MARKERS)
    if "database" in routes and not has_data_source and not explicitly_requests_database:
        routes = [route for route in routes if route != "database"]
        if "document" not in routes:
            routes.insert(0, "document")
    persona_slug = (
        "financial-analyst"
        if any(route in routes for route in ("database", "math"))
        else plan.persona_slug
    )
    return AgentPlan(persona_slug, routes, plan.calculation)


class AgentState(TypedDict):
    run_id: uuid.UUID
    trace_id: str
    question: str
    knowledge_base_id: uuid.UUID
    requested_persona_id: uuid.UUID | None
    requested_data_source_id: uuid.UUID | None
    persona: NotRequired[PersonaDefinition]
    plan: NotRequired[AgentPlan]
    routes: NotRequired[list[str]]
    llm: NotRequired[LlmProvider]
    rag_result: NotRequired[RagResult]
    database_result: NotRequired[DatabaseQueryResult]
    database_answer: NotRequired[str]
    calculation: NotRequired[CalculationResult]
    answer: NotRequired[str]
    support: NotRequired[str]
    suggestions: NotRequired[list[str]]


@dataclass(frozen=True, slots=True)
class GraphResult:
    answer: str
    support: str
    persona: PersonaDefinition
    routes: list[str]
    provider: str
    model: str
    rag: RagResult | None
    database: DatabaseQueryResult | None
    calculations: list[CalculationResult]
    suggestions: list[str]
    prompt_version: str


class DocumentRagGraph:
    def __init__(
        self,
        *,
        rag: RagService,
        traces: TraceService,
        llms: LlmRegistry,
        personas: PersonaRegistry,
        database: PostgresConnector,
        math: MathService,
    ) -> None:
        self._rag = rag
        self._traces = traces
        self._llms = llms
        self._personas = personas
        self._database = database
        self._math = math

    async def run(
        self,
        *,
        session: AsyncSession,
        context: TenantContext,
        run_id: uuid.UUID,
        trace_id: str,
        knowledge_base_id: uuid.UUID,
        question: str,
        persona_id: uuid.UUID | None = None,
        data_source_id: uuid.UUID | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> GraphResult:
        llm = self._llms.resolve(provider, model)

        async def emit(
            event_type: str, stage: str, summary: dict[str, object] | None = None
        ) -> None:
            await self._traces.emit(
                run_id=run_id, event_type=event_type, stage=stage, safe_summary=summary
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
            return {"question": normalized, "llm": llm}

        async def persona_selector(state: AgentState) -> dict[str, object]:
            await emit("persona_selection_started", "persona_selector")
            plan = normalize_plan_for_selected_sources(
                await state["llm"].plan(state["question"]),
                question=state["question"],
                has_data_source=state["requested_data_source_id"] is not None,
            )
            requested_persona_id = state["requested_persona_id"]
            persona = (
                self._personas.get_by_id(requested_persona_id)
                if requested_persona_id
                else self._personas.get_by_slug(plan.persona_slug)
            )
            selection_mode = "manual" if requested_persona_id else "auto"
            if not requested_persona_id and set(plan.routes) - set(persona.allowed_routes):
                persona = self._personas.get_by_slug("general-assistant")
                selection_mode = "auto_policy_fallback"
            await emit(
                "persona_selected",
                "persona_selector",
                {
                    "persona": persona.slug,
                    "selection_mode": selection_mode,
                },
            )
            return {"persona": persona, "plan": plan}

        async def router(state: AgentState) -> dict[str, object]:
            routes = list(dict.fromkeys(state["plan"].routes))
            unauthorized = set(routes) - set(state["persona"].allowed_routes)
            if unauthorized:
                raise AppError(
                    status_code=422,
                    code="PERSONA_ROUTE_NOT_ALLOWED",
                    message="The selected persona does not permit the required route.",
                )
            await emit(
                "router_completed",
                "intent_router",
                {"route": "+".join(routes), "route_count": len(routes)},
            )
            return {"routes": routes}

        async def document_node(state: AgentState) -> dict[str, object]:
            if "document" not in state["routes"]:
                return {}
            result = await self._rag.answer(
                session=session,
                context=context,
                knowledge_base_id=state["knowledge_base_id"],
                question=state["question"],
                llm=state["llm"],
                persona_behavior=state["persona"].system_behavior,
                trace=emit,
            )
            await emit(
                "citation_validation_completed",
                "document_node",
                {"citation_count": len(result.sources), "support": result.support},
            )
            return {"rag_result": result}

        async def database_node(state: AgentState) -> dict[str, object]:
            if "database" not in state["routes"]:
                return {}
            if re.search(
                r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|call|execute)\b",
                state["question"],
                flags=re.IGNORECASE,
            ):
                raise AppError(
                    status_code=422,
                    code="UNSAFE_DATABASE_REQUEST",
                    message="Database mutation or administrative requests are prohibited.",
                )
            statement = select(DataSource).where(
                DataSource.organization_id == context.organization_id,
                DataSource.knowledge_base_id == state["knowledge_base_id"],
                DataSource.is_active.is_(True),
            )
            if state["requested_data_source_id"]:
                statement = statement.where(DataSource.id == state["requested_data_source_id"])
            source = await session.scalar(statement.order_by(DataSource.created_at).limit(1))
            if source is None:
                raise AppError(
                    status_code=422,
                    code="DATA_SOURCE_REQUIRED",
                    message="No authorized database source is available for this knowledge base.",
                )
            await emit("database_query_started", "database_node", {"source_type": source.kind})
            schema = await self._database.discover_schema(source)
            sql = await state["llm"].generate_sql(
                SqlGenerationRequest(
                    state["question"],
                    source.allowed_schema,
                    {table.name: table.columns for table in schema},
                )
            )
            result = await self._database.execute(source, sql)
            answer = await state["llm"].explain_database_result(state["question"], result.rows)
            await emit(
                "database_query_completed",
                "database_node",
                {"row_count": result.row_count, "table_count": len(result.tables)},
            )
            return {"database_result": result, "database_answer": answer}

        async def math_node(state: AgentState) -> dict[str, object]:
            if "math" not in state["routes"]:
                return {}
            request = state["plan"].calculation
            if request is None:
                raise AppError(
                    status_code=422,
                    code="INVALID_CALCULATION",
                    message="The calculation inputs could not be determined safely.",
                )
            if not request.values and "database_result" in state:
                values = [
                    float(value)
                    for row in state["database_result"].rows
                    for value in row.values()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                ][:100]
                request = CalculationRequest(request.operation, values, request.unit)
            await emit("calculation_started", "math_node", {"operation": request.operation})
            result = self._math.calculate(request)
            await emit("calculation_completed", "math_node", {"operation": result.operation})
            return {"calculation": result}

        async def suggestion_node(state: AgentState) -> dict[str, object]:
            suggestions = self._suggestions(
                state["persona"].slug,
                state["routes"],
                "rag_result" in state and state["rag_result"].support == "grounded",
            )
            await emit(
                "suggestion_generation_completed",
                "suggestion_node",
                {"suggestion_count": len(suggestions)},
            )
            return {"suggestions": suggestions}

        async def formatter(state: AgentState) -> dict[str, object]:
            parts: list[str] = []
            grounded = False
            if "rag_result" in state and state["rag_result"].support == "grounded":
                parts.append(state["rag_result"].answer)
                grounded = True
            if "database_answer" in state:
                parts.append(state["database_answer"])
                grounded = True
            if "calculation" in state:
                calc = state["calculation"]
                suffix = f" {calc.unit}" if calc.unit else ""
                parts.append(
                    f"Deterministic {calc.operation.replace('_', ' ')} result: "
                    f"{calc.result:g}{suffix}."
                )
                grounded = True
            answer = "\n\n".join(parts) if parts else UNANSWERABLE
            return {"answer": answer, "support": "grounded" if grounded else "unanswerable"}

        builder = StateGraph(AgentState)
        for name, node in (
            ("security_input_guard", guard),
            ("persona_selector", persona_selector),
            ("router", router),
            ("document_node", document_node),
            ("database_node", database_node),
            ("math_node", math_node),
            ("suggestion_node", suggestion_node),
            ("formatter", formatter),
        ):
            builder.add_node(name, node)
        builder.add_edge(START, "security_input_guard")
        builder.add_edge("security_input_guard", "persona_selector")
        builder.add_edge("persona_selector", "router")
        builder.add_edge("router", "document_node")
        builder.add_edge("document_node", "database_node")
        builder.add_edge("database_node", "math_node")
        builder.add_edge("math_node", "suggestion_node")
        builder.add_edge("suggestion_node", "formatter")
        builder.add_edge("formatter", END)
        try:
            final = await builder.compile().ainvoke(
                AgentState(
                    run_id=run_id,
                    trace_id=trace_id,
                    question=question,
                    knowledge_base_id=knowledge_base_id,
                    requested_persona_id=persona_id,
                    requested_data_source_id=data_source_id,
                )
            )
        except Exception as exc:
            await emit(
                "error",
                "workflow",
                {"error_code": exc.code if isinstance(exc, AppError) else "WORKFLOW_FAILED"},
            )
            raise
        rag = final.get("rag_result")
        database = final.get("database_result")
        calculations = [final["calculation"]] if "calculation" in final else []
        await emit(
            "response_completed",
            "formatter",
            {"support": final["support"], "citation_count": len(rag.sources) if rag else 0},
        )
        return GraphResult(
            final["answer"],
            final["support"],
            final["persona"],
            final["routes"],
            llm.provider_name,
            llm.model,
            rag,
            database,
            calculations,
            final["suggestions"],
            rag.prompt_version if rag else "dynamic-intelligence-v1",
        )

    @staticmethod
    def _suggestions(persona: str, routes: list[str], has_document_evidence: bool) -> list[str]:
        suggestions: list[str] = []
        if persona == "legal-advisor" and has_document_evidence:
            suggestions.append("Would you like me to compare related clauses in the document?")
        if persona == "financial-analyst" and ("database" in routes or "math" in routes):
            suggestions.append("Would you like a related year-over-year calculation?")
        if "document" in routes and has_document_evidence:
            suggestions.append("Would you like a summary of the cited document section?")
        if "database" in routes:
            suggestions.append("Would you like the result grouped by an approved field?")
        return suggestions[:4] or ["Would you like to ask a grounded follow-up question?"]
