from __future__ import annotations

import time
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.ai_lab.service import AiLabService
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.db.models import Experiment
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.evaluation.service import EvaluationService
from dynamic_agentic_api.llm.registry import LlmRegistry
from dynamic_agentic_api.telemetry import observed_stage


def _bounded_integer(value: object, *, default: int, minimum: int, maximum: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise AppError(
            status_code=422,
            code="INVALID_EVALUATION_PARAMETER",
            message="Numeric evaluation parameters must contain a valid integer.",
        )
    try:
        parsed = int(value)
    except ValueError as exc:
        raise AppError(
            status_code=422,
            code="INVALID_EVALUATION_PARAMETER",
            message="Numeric evaluation parameters must contain a valid integer.",
        ) from exc
    return min(max(parsed, minimum), maximum)


class ExperimentService:
    def __init__(
        self, *, lab: AiLabService, evaluation: EvaluationService, llms: LlmRegistry
    ) -> None:
        self._lab = lab
        self._evaluation = evaluation
        self._llms = llms

    async def run_lab(
        self,
        session: AsyncSession,
        context: TenantContext,
        *,
        lab_type: str,
        algorithm: str,
        dataset: str,
        parameters: dict[str, object],
        seed: int,
    ) -> Experiment:
        experiment = Experiment(
            organization_id=context.organization_id,
            user_id=context.user_id,
            lab_type=lab_type,
            algorithm=algorithm,
            dataset=dataset,
            dataset_version="builtin-v1",
            parameters=parameters,
            random_seed=seed,
            status="running",
            started_at=datetime.now(UTC),
        )
        session.add(experiment)
        await session.commit()
        started = time.perf_counter()
        try:
            with observed_stage("Experiment execution"):
                result = await self._lab.run(
                    lab_type=lab_type,
                    algorithm=algorithm,
                    dataset=dataset,
                    parameters=parameters,
                    seed=seed,
                )
            experiment.metrics = result.metrics
            experiment.artifact_metadata = result.artifact_metadata
            experiment.library_versions = result.library_versions
            experiment.status = "completed"
        except Exception as exc:
            experiment.status = "failed"
            experiment.error_code = exc.code if isinstance(exc, AppError) else "EXPERIMENT_FAILED"
            experiment.completed_at = datetime.now(UTC)
            experiment.duration_ms = round((time.perf_counter() - started) * 1000)
            await session.commit()
            raise
        experiment.completed_at = datetime.now(UTC)
        experiment.duration_ms = round((time.perf_counter() - started) * 1000)
        await session.commit()
        await session.refresh(experiment)
        return experiment

    async def run_evaluation(
        self,
        session: AsyncSession,
        context: TenantContext,
        *,
        benchmark: str,
        parameters: dict[str, object],
        seed: int,
    ) -> Experiment:
        lab_type = (
            "rag_evaluation"
            if benchmark in {"rag", "rag_comparison"}
            else "security_evaluation"
            if benchmark in {"database", "security"}
            else "agent_evaluation"
        )
        experiment = Experiment(
            organization_id=context.organization_id,
            user_id=context.user_id,
            lab_type=lab_type,
            algorithm=benchmark,
            dataset="deterministic-evaluation-suite",
            dataset_version="evaluation-v1",
            parameters=parameters,
            random_seed=seed,
            status="running",
            started_at=datetime.now(UTC),
            library_versions={},
            artifact_metadata={"production_state_mutated": False},
        )
        session.add(experiment)
        await session.commit()
        started = time.perf_counter()
        try:
            if benchmark == "rag":
                metrics = self._evaluation.built_in_rag_benchmark(
                    _bounded_integer(parameters.get("top_k"), default=3, minimum=1, maximum=20)
                )
            elif benchmark == "rag_comparison":
                raw = parameters.get("configurations", [])
                configurations = []
                if isinstance(raw, list):
                    for item in raw[:8]:
                        if not isinstance(item, dict):
                            continue
                        configurations.append(
                            {
                                "chunk_size": _bounded_integer(
                                    item.get("chunk_size"),
                                    default=200,
                                    minimum=50,
                                    maximum=2000,
                                ),
                                "chunk_overlap": _bounded_integer(
                                    item.get("chunk_overlap"),
                                    default=20,
                                    minimum=0,
                                    maximum=1999,
                                ),
                                "top_k": _bounded_integer(
                                    item.get("top_k"),
                                    default=2,
                                    minimum=1,
                                    maximum=10,
                                ),
                            }
                        )
                if not configurations:
                    raise AppError(
                        status_code=422,
                        code="INVALID_EVALUATION_PARAMETER",
                        message="RAG comparison requires at least one valid configuration.",
                    )
                metrics = self._evaluation.rag_configuration_comparison(configurations)
            elif benchmark == "persona_router":
                metrics = await self._evaluation.persona_router_benchmark(
                    self._llms.resolve(None, None)
                )
            elif benchmark == "database":
                metrics = self._evaluation.database_security_benchmark()
            elif benchmark == "math":
                metrics = self._evaluation.math_benchmark()
            elif benchmark == "security":
                metrics = self._evaluation.security_benchmark()
            elif benchmark == "llm":
                metrics = await self._evaluation.llm_benchmark(self._llms.resolve(None, None))
            elif benchmark == "prompts":
                metrics = await self._evaluation.prompt_benchmark(self._llms.resolve(None, None))
            else:
                raise AppError(
                    status_code=422,
                    code="UNSUPPORTED_BENCHMARK",
                    message="The selected benchmark is not allowlisted.",
                )
            experiment.metrics = metrics
            experiment.status = "completed"
        except Exception as exc:
            experiment.status = "failed"
            experiment.error_code = exc.code if isinstance(exc, AppError) else "EVALUATION_FAILED"
            experiment.completed_at = datetime.now(UTC)
            experiment.duration_ms = round((time.perf_counter() - started) * 1000)
            await session.commit()
            raise
        experiment.completed_at = datetime.now(UTC)
        experiment.duration_ms = round((time.perf_counter() - started) * 1000)
        await session.commit()
        await session.refresh(experiment)
        return experiment
