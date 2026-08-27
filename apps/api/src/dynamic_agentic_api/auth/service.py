from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from dynamic_agentic_api.auth.domain import AuthenticatedUser, TenantContext
from dynamic_agentic_api.db.models import OrganizationMembership, Role
from dynamic_agentic_api.errors import AppError


class AuthorizationService:
    async def resolve_tenant_context(
        self,
        session: AsyncSession,
        user: AuthenticatedUser,
        organization_id: uuid.UUID,
    ) -> TenantContext:
        statement = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user.user_id,
                OrganizationMembership.status == "active",
            )
            .options(selectinload(OrganizationMembership.roles).selectinload(Role.permissions))
        )
        membership = await session.scalar(statement)
        if membership is None:
            raise AppError(
                status_code=403,
                code="TENANT_ACCESS_DENIED",
                message="You do not have access to this organization.",
            )
        role_names = frozenset(role.name for role in membership.roles)
        permissions = frozenset(
            permission.code for role in membership.roles for permission in role.permissions
        )
        return TenantContext(
            organization_id=organization_id,
            user_id=user.user_id,
            membership_id=membership.id,
            role_names=role_names,
            permissions=permissions,
        )

    @staticmethod
    def require_permission(context: TenantContext, permission: str) -> None:
        if not context.has_permission(permission):
            raise AppError(
                status_code=403,
                code="PERMISSION_DENIED",
                message="You do not have permission to perform this action.",
            )
