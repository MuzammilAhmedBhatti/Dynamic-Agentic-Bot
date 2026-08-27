from __future__ import annotations

from dynamic_agentic_api.db.session import engine
from sqlalchemy import inspect, text


async def test_database_connection_and_foundation_migration() -> None:
    async with engine.connect() as connection:
        assert (await connection.scalar(text("SELECT 1"))) == 1
        table_names = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )
    assert {
        "alembic_version",
        "organizations",
        "users",
        "organization_memberships",
        "roles",
        "permissions",
        "role_permissions",
        "membership_roles",
    }.issubset(set(table_names))
