from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.models import User
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.schemas import TestSessionRequest, TestSessionResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/test-session", response_model=TestSessionResponse)
async def create_test_session(
    payload: TestSessionRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TestSessionResponse:
    settings = get_settings()
    if settings.app_env != "test" or settings.auth_mode != "test":
        raise AppError(
            status_code=404,
            code="NOT_FOUND",
            message="The requested resource was not found.",
        )
    user = await session.get(User, payload.user_id)
    if user is None or not user.is_active:
        raise AppError(
            status_code=401,
            code="INVALID_TEST_IDENTITY",
            message="The test identity is invalid.",
        )
    response.set_cookie(
        key="dynamic_agentic_test_user",
        value=str(user.id),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
        path="/",
    )
    return TestSessionResponse(user_id=user.id)
