from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.schemas import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


def health_payload() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(service=settings.app_name, environment=settings.app_env)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return health_payload()


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReadinessResponse:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise AppError(
            status_code=503,
            code="DATABASE_NOT_READY",
            message="The database is not ready.",
            retryable=True,
        ) from exc
    return ReadinessResponse()
