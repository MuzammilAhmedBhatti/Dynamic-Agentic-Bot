from __future__ import annotations

import uuid

import httpx
import pytest
from dynamic_agentic_api.db.models import (
    MembershipRole,
    Organization,
    OrganizationMembership,
    Permission,
    Role,
    RolePermission,
    User,
)
from dynamic_agentic_api.db.session import async_session_factory
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


async def seed_membership(*, grant_read: bool = True) -> tuple[uuid.UUID, uuid.UUID]:
    async with async_session_factory() as session:
        organization = Organization(name="Acme", slug=f"acme-{uuid.uuid4().hex[:8]}")
        user = User(
            identity_provider="explicit-test-provider",
            external_subject=uuid.uuid4().hex,
            email_normalized=f"user-{uuid.uuid4().hex[:8]}@example.com",
        )
        session.add_all([organization, user])
        await session.flush()
        membership = OrganizationMembership(
            organization_id=organization.id, user_id=user.id
        )
        role = Role(organization_id=organization.id, name="reader")
        session.add_all([membership, role])
        await session.flush()
        session.add(
            MembershipRole(
                membership_id=membership.id,
                role_id=role.id,
                organization_id=organization.id,
            )
        )
        if grant_read:
            permission = await session.scalar(
                select(Permission).where(Permission.code == "organization.read")
            )
            if permission is None:
                permission = Permission(
                    code="organization.read", description="Read organization context"
                )
                session.add(permission)
                await session.flush()
            session.add(RolePermission(role_id=role.id, permission_id=permission.id))
        await session.commit()
        return organization.id, user.id


async def test_authorized_member_receives_server_derived_context(
    client: httpx.AsyncClient,
) -> None:
    organization_id, user_id = await seed_membership()
    response = await client.get(
        f"/api/v1/organizations/{organization_id}/context",
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["organization"]["id"] == str(organization_id)
    assert body["user_id"] == str(user_id)
    assert body["roles"] == ["reader"]
    assert body["permissions"] == ["organization.read"]


async def test_permission_denial(client: httpx.AsyncClient) -> None:
    organization_id, user_id = await seed_membership(grant_read=False)
    response = await client.get(
        f"/api/v1/organizations/{organization_id}/context",
        headers={"X-Test-User-ID": str(user_id)},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


async def test_cross_tenant_access_is_denied(client: httpx.AsyncClient) -> None:
    organization_id, _ = await seed_membership()
    _, other_user_id = await seed_membership()
    response = await client.get(
        f"/api/v1/organizations/{organization_id}/context",
        headers={"X-Test-User-ID": str(other_user_id)},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "TENANT_ACCESS_DENIED"


async def test_cross_tenant_role_assignment_is_rejected_by_database() -> None:
    async with async_session_factory() as session:
        first = Organization(name="First", slug=f"first-{uuid.uuid4().hex[:8]}")
        second = Organization(name="Second", slug=f"second-{uuid.uuid4().hex[:8]}")
        user = User(
            identity_provider="explicit-test-provider",
            external_subject=uuid.uuid4().hex,
            email_normalized=f"cross-{uuid.uuid4().hex[:8]}@example.com",
        )
        session.add_all([first, second, user])
        await session.flush()
        membership = OrganizationMembership(organization_id=first.id, user_id=user.id)
        foreign_role = Role(organization_id=second.id, name="foreign")
        session.add_all([membership, foreign_role])
        await session.flush()
        session.add(
            MembershipRole(
                membership_id=membership.id,
                role_id=foreign_role.id,
                organization_id=first.id,
            )
        )
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_invalid_organization_id_uses_validation_envelope(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/organizations/not-a-uuid/context",
        headers={"X-Test-User-ID": str(uuid.uuid4())},
    )
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert "input" not in response.text
    assert "trace_id" in body
