from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from dynamic_agentic_api.auth.domain import AuthenticatedUser, TenantContext
from dynamic_agentic_api.auth.providers import IdentityProvider, build_identity_provider
from dynamic_agentic_api.auth.service import AuthorizationService
from dynamic_agentic_api.config import get_settings
from dynamic_agentic_api.db.session import get_db_session

identity_provider: IdentityProvider = build_identity_provider(get_settings())
authorization_service = AuthorizationService()


async def get_authenticated_user(request: Request) -> AuthenticatedUser:
    return await identity_provider.authenticate(request)


async def get_tenant_context(
    organization_id: uuid.UUID,
    user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantContext:
    return await authorization_service.resolve_tenant_context(session, user, organization_id)
