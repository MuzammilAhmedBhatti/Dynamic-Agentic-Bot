from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.ai_lab.service import ALGORITHMS
from dynamic_agentic_api.auth.dependencies import authorization_service, get_tenant_context
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.models import Experiment
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.observability import get_logger
from dynamic_agentic_api.schemas import (
    EvaluationRunCreate,
    ExperimentResponse,
    LabCatalogResponse,
    LabExperimentCreate,
)
from dynamic_agentic_api.services import get_ai_services
from dynamic_agentic_api.telemetry import observed_stage

router = APIRouter(prefix="/organizations/{organization_id}", tags=["experiments"])
logger = get_logger()


@router.get("/ai-lab/catalog", response_model=LabCatalogResponse)
async def lab_catalog(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
) -> LabCatalogResponse:
    authorization_service.require_permission(context, "chat.execute")
    settings = get_settings()
    return LabCatalogResponse(
        algorithms={key: list(value) for key, value in ALGORITHMS.items()},
        datasets=["generated_profile_v1", "iris", "diabetes", "sentiment_fixture_v1"],
        limits={
            "max_dataset_rows": settings.lab_max_dataset_rows,
            "max_epochs": settings.lab_max_epochs,
            "max_runtime_seconds": settings.lab_max_runtime_seconds,
            "max_concurrent_experiments": settings.lab_max_concurrent_experiments,
        },
    )


@router.post("/ai-lab/experiments", response_model=ExperimentResponse, status_code=201)
async def run_lab_experiment(
    payload: LabExperimentCreate,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExperimentResponse:
    authorization_service.require_permission(context, "chat.execute")
    experiment = await get_ai_services().experiments.run_lab(
        session,
        context,
        lab_type=payload.lab_type,
        algorithm=payload.algorithm,
        dataset=payload.dataset,
        parameters=payload.parameters,
        seed=payload.random_seed,
    )
    logger.info(
        "ai_lab_experiment_completed",
        experiment_id=str(experiment.id),
        tenant_id=str(context.organization_id),
        lab_type=experiment.lab_type,
        algorithm=experiment.algorithm,
        duration_ms=experiment.duration_ms,
        status=experiment.status,
    )
    return ExperimentResponse.model_validate(experiment)


@router.post("/evaluations", response_model=ExperimentResponse, status_code=201)
async def run_evaluation(
    payload: EvaluationRunCreate,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExperimentResponse:
    authorization_service.require_permission(context, "chat.execute")
    with observed_stage("Evaluation execution"):
        experiment = await get_ai_services().experiments.run_evaluation(
            session,
            context,
            benchmark=payload.benchmark,
            parameters=payload.parameters,
            seed=payload.random_seed,
        )
    logger.info(
        "evaluation_completed",
        experiment_id=str(experiment.id),
        tenant_id=str(context.organization_id),
        benchmark=experiment.algorithm,
        duration_ms=experiment.duration_ms,
        status=experiment.status,
    )
    return ExperimentResponse.model_validate(experiment)


@router.get("/experiments", response_model=list[ExperimentResponse])
async def list_experiments(
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[ExperimentResponse]:
    authorization_service.require_permission(context, "chat.execute")
    rows = (
        await session.scalars(
            select(Experiment)
            .where(Experiment.organization_id == context.organization_id)
            .order_by(Experiment.created_at.desc())
            .limit(limit)
        )
    ).all()
    return [ExperimentResponse.model_validate(row) for row in rows]


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: uuid.UUID,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExperimentResponse:
    authorization_service.require_permission(context, "chat.execute")
    experiment = await session.scalar(
        select(Experiment).where(
            Experiment.id == experiment_id,
            Experiment.organization_id == context.organization_id,
        )
    )
    if experiment is None:
        raise AppError(
            status_code=404,
            code="EXPERIMENT_NOT_FOUND",
            message="The experiment was not found.",
        )
    return ExperimentResponse.model_validate(experiment)
