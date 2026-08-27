from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.dependencies import (
    authorization_service,
    get_tenant_context,
)
from dynamic_agentic_api.auth.domain import TenantContext
from dynamic_agentic_api.db.models import Organization
from dynamic_agentic_api.db.session import get_db_session
from dynamic_agentic_api.errors import AppError
from dynamic_agentic_api.schemas import OrganizationResponse, TenantContextResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/{organization_id}/context", response_model=TenantContextResponse)
async def organization_context(
    organization_id: uuid.UUID,
    context: Annotated[TenantContext, Depends(get_tenant_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantContextResponse:
    authorization_service.require_permission(context, "organization.read")
    organization = await session.get(Organization, organization_id)
    if organization is None or organization.status != "active":
        raise AppError(
            status_code=404,
            code="ORGANIZATION_NOT_FOUND",
            message="The organization was not found.",
        )
    return TenantContextResponse(
        organization=OrganizationResponse.model_validate(organization),
        user_id=context.user_id,
        membership_id=context.membership_id,
        roles=sorted(context.role_names),
        permissions=sorted(context.permissions),
    )
