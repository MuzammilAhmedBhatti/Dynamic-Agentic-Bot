from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from dynamic_agentic_api.config import get_settings
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


async def bootstrap() -> None:
    settings = get_settings()
    if settings.app_env != "test" or settings.auth_mode != "test":
        raise SystemExit("Development bootstrap requires APP_ENV=test and AUTH_MODE=test.")

    async with async_session_factory() as session:
        existing = (
            await session.execute(
                select(Organization, User)
                .join(
                    OrganizationMembership,
                    OrganizationMembership.organization_id == Organization.id,
                )
                .join(User, User.id == OrganizationMembership.user_id)
                .where(
                    Organization.slug.like("local-demo-%"),
                    Organization.status == "active",
                    OrganizationMembership.status == "active",
                    User.identity_provider == "explicit-test-provider",
                    User.is_active.is_(True),
                )
                .order_by(Organization.created_at)
                .limit(1)
            )
        ).first()
        if existing is not None:
            organization, user = existing
            print("Reusing the existing local development organization and user.")
            print(f"Organization ID: {organization.id}")
            print(f"Local test user ID: {user.id}")
            return
        organization = Organization(name="Local Demo", slug=f"local-demo-{uuid.uuid4().hex[:8]}")
        user = User(
            identity_provider="explicit-test-provider",
            external_subject=uuid.uuid4().hex,
            email_normalized=f"local-{uuid.uuid4().hex[:8]}@example.test",
        )
        session.add_all([organization, user])
        await session.flush()
        membership = OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
        )
        role = Role(organization_id=organization.id, name="local-owner")
        session.add_all([membership, role])
        await session.flush()
        session.add(
            MembershipRole(
                membership_id=membership.id,
                role_id=role.id,
                organization_id=organization.id,
            )
        )
        for code in ("knowledge_base.read", "knowledge_base.write", "chat.execute"):
            permission = await session.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=code)
                session.add(permission)
                await session.flush()
            session.add(RolePermission(role_id=role.id, permission_id=permission.id))
        await session.commit()

    print(f"Organization ID: {organization.id}")
    print(f"Local test user ID: {user.id}")


if __name__ == "__main__":
    asyncio.run(bootstrap())
